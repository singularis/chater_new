package com.chamini;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Properties;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.json.JSONObject;

public class GoogleGemini {

    private static final Logger LOGGER = Logger.getLogger(GoogleGemini.class.getName());
    private static final String API_MODEL = System.getenv("GEMINI_MODEL");
    private static final String API_KEY = System.getenv("API_KEY");
    private static final String BOOTSTRAP_SERVER = System.getenv("BOOTSTRAP_SERVER");
    private static final String TOPIC = "gemini-send";


    public static void main(String[] args) {
        if (API_KEY == null || API_KEY.isEmpty()) {
            LOGGER.log(Level.SEVERE, "API_KEY environment variable is not set");
            return;
        }

        KafkaConsumer consumer = new KafkaConsumer(BOOTSTRAP_SERVER, "chamini", TOPIC);
        KafkaProducerUtil producer = new KafkaProducerUtil(BOOTSTRAP_SERVER) {
            @Override
            protected KafkaProducer<String, String> createProducer(Properties props) {
                return null;
            }
        };

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            LOGGER.info("Shutdown initiated...");
            consumer.close();
            producer.close();
        }));

        while (true) {
            String message = consumer.consumeMessage();
            if (message != null && !message.isEmpty()) {
                processMessage(message, producer);
            }
        }
    }

    private static void processMessage(String message, KafkaProducerUtil producer) {
        String uuid;
        String question;

        try {
            JSONObject jsonObject = new JSONObject(message);
            uuid = jsonObject.getString("key");
            JSONObject valueObject = jsonObject.getJSONObject("value");
            question = valueObject.getString("question");
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to extract question from message", e);
            return;
        }

        try {
            HttpURLConnection connection = getHttpURLConnection(question);

            int responseCode = connection.getResponseCode();
            LOGGER.log(Level.INFO, "Response Code: {0}", responseCode);

            if (responseCode == HttpURLConnection.HTTP_OK) {
                try (Scanner scanner = new Scanner(connection.getInputStream())) {
                    String responseBody = scanner.useDelimiter("\\A").next();
                    LOGGER.log(Level.INFO, "Response Body: {0}", responseBody);

                    String text = JsonParser.extractText(responseBody);
                    if (text != null) {
                        LOGGER.log(Level.INFO, "Extracted Text: {0}", text);
                        producer.sendMessage("gemini-response", uuid, text);
                    }
                }
            } else {
                try (Scanner scanner = new Scanner(connection.getErrorStream())) {
                    String errorResponse = scanner.useDelimiter("\\A").next();
                    LOGGER.log(Level.WARNING, "Request failed with response code: {0} and error: {1}", new Object[]{responseCode, errorResponse});
                    producer.sendMessage("gemini-response", uuid, errorResponse);
                }
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Exception occurred", e);
        }
    }

    public static HttpURLConnection getHttpURLConnection(String question) throws IOException {
        URL url = new URL("https://generativelanguage.googleapis.com/v1beta/models/" + API_MODEL + ":generateContent?key=" + API_KEY);

        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);

        String jsonInputString = String.format("{\"contents\":[{\"parts\":[{\"text\":\"%s\"}]}]}", question);

        try (OutputStream os = connection.getOutputStream()) {
            byte[] input = jsonInputString.getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }
        return connection;
    }
}

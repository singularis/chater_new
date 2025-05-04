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
    private static final String GEMINI_THINK_MODEL = System.getenv("GEMINI_THINK_MODEL");

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
        String model;
        boolean think;
        String userEmail = null;

        try {
            JSONObject jsonObject = new JSONObject(message);
            uuid = jsonObject.getString("key");
            Object value = jsonObject.get("value");
            
            // Handle both string and JSON object values
            if (value instanceof String) {
                question = (String) value;
                think = false;
            } else {
                JSONObject valueObject = (JSONObject) value;
                question = valueObject.getString("question");
                think = Boolean.parseBoolean(valueObject.optString("think", "false"));
                if (valueObject.has("user_email")) {
                    userEmail = valueObject.getString("user_email");
                }
            }
            
            if (think) {
                model = GEMINI_THINK_MODEL;
            } else {
                model = API_MODEL;
            }
            LOGGER.log(Level.INFO, "Model: {0}", model);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to extract question from message", e);
            return;
        }

        try {
            HttpURLConnection connection = getHttpURLConnection(question, model);

            int responseCode = connection.getResponseCode();
            LOGGER.log(Level.INFO, "Response Code: {0}", responseCode);

            if (responseCode == HttpURLConnection.HTTP_OK) {
                try (Scanner scanner = new Scanner(connection.getInputStream())) {
                    String responseBody = scanner.useDelimiter("\\A").next();
                    LOGGER.log(Level.INFO, "Response Body: {0}", responseBody);

                    String text = JsonParser.extractText(responseBody);
                    if (text != null) {
                        LOGGER.log(Level.INFO, "Extracted Text: {0}", text);
                        String cleanedText = text.replace("```json", "").replace("```", "").trim();
                        
                        if (userEmail != null) {
                            try {
                                JSONObject valueResponse = new JSONObject(cleanedText);
                                valueResponse.put("user_email", userEmail);
                                producer.sendMessage("gemini-response", uuid, valueResponse);
                            } catch (Exception e) {
                                JSONObject valueResponse = new JSONObject();
                                valueResponse.put("response", cleanedText);
                                valueResponse.put("user_email", userEmail);
                                producer.sendMessage("gemini-response", uuid, valueResponse);
                            }
                        } else {
                            try {
                                producer.sendMessage("gemini-response", uuid, new JSONObject(cleanedText));
                            } catch (Exception e) {
                                producer.sendMessage("gemini-response", uuid, cleanedText);
                            }
                        }
                    }
                }
            } else {
                try (Scanner scanner = new Scanner(connection.getErrorStream())) {
                    String errorResponse = scanner.useDelimiter("\\A").next();
                    LOGGER.log(Level.WARNING, "Request failed with response code: {0} and error: {1}", new Object[]{responseCode, errorResponse});
                    JSONObject errorObject = new JSONObject();
                    errorObject.put("key", uuid);
                    JSONObject errorValue = new JSONObject();
                    errorValue.put("error", errorResponse);
                    if (userEmail != null) {
                        errorValue.put("user_email", userEmail);
                    }
                    errorObject.put("value", errorValue);
                    producer.sendMessage("gemini-response", uuid, errorObject.toString());
                }
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Exception occurred", e);
        }
    }

    public static HttpURLConnection getHttpURLConnection(String question, String model) throws IOException {
        URL url = new URL("https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + API_KEY);

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

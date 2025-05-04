package org.chater;

import java.io.IOException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;


public class Main {
    private static final Logger logger = LogManager.getLogger(Main.class);
    public static void main(String[] args) throws IOException, InterruptedException {
        logger.info("Chater vision starting...");
        KafkaConsume newConsumer = new KafkaConsume();
        newConsumer.CreateConsumer("chater-vision", "chater-vision-group");
        KafkaConsume visionConsumer = new KafkaConsume();
        visionConsumer.CreateConsumer("gemini-response", "chater");
        KafkaProduce visionProducer = new KafkaProduce();
        visionProducer.CreateProducer();
        while (true) {
            try {
                String message = newConsumer.Consume();
                if (message!=null &&!message.isEmpty()) {
                    JSONObject initialMessage = new JSONObject(message);
                    String userEmail = initialMessage.getJSONObject("value").getString("user_email");
                    processMessage(message, visionProducer, userEmail);
                    responder(visionProducer, visionConsumer, userEmail);
                }
            }
            catch (Exception e) {
                logger.error(e);
                visionProducer.close();
                throw new IOException("Error consuming message", e);
            }
        }
    }
    public static void processMessage(String message, KafkaProduce visionProducer, String userEmail) throws IOException, InterruptedException {
        String text;
        JSONObject jsonObject = new JSONObject(message);
        JSONObject valueObject = jsonObject.getJSONObject("value");
        String prompt = valueObject.getString("prompt");
        String uuid = jsonObject.getString("key");
        String photo = valueObject.getString("photo");
        text = DetectText.detectText(photo);
        logger.info("Detected text: {}", text);
        JSONObject photoQuestion = new JSONObject();
        String question = prompt + text;
        photoQuestion.put("key", uuid);
        JSONObject addressObject = new JSONObject();
        addressObject.put("question", question);
        addressObject.put("user_email", userEmail);
        photoQuestion.put("value", addressObject);
        visionProducer.SendMessage(photoQuestion.toString(), "gemini-send");
    }
    public static void responder(KafkaProduce visionProducer, KafkaConsume visionConsumer, String userEmail) throws InterruptedException {
        String message;
        String cleanedJson;
        logger.info("Chater vision responder");
        long startTime = System.currentTimeMillis();
        while (true) {
            message = visionConsumer.Consume();
            if (message!=null &&!message.isEmpty()) {
                logger.info("Consumed message: {}", message);
                cleanedJson = message
                        .replace("```json", "")
                        .replace("```", "")
                        .trim();
                logger.info("Cleaned json: {}", cleanedJson);
                JSONObject jsonObject = new JSONObject(cleanedJson);
                String uuid = jsonObject.getString("key");
                JSONObject valueObject = jsonObject.getJSONObject("value");

                JSONObject responseObject = new JSONObject();
                responseObject.put("key", uuid);
                responseObject.put("value", valueObject);
                logger.info("Response after weight processing: {}", responseObject);
                visionProducer.SendMessage(responseObject.toString(), "photo-analysis-response");
                break;
            }
            if (System.currentTimeMillis()-startTime>60000) {
                logger.info("No message received within 60 seconds. Exiting and waiting for next photo");
                break;
            }
        }
    }
}
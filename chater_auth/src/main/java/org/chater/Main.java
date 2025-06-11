package org.chater;

import java.io.IOException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;


public class Main {
    private static final Logger logger = LogManager.getLogger(Main.class);
    
    public static void main(String[] args) throws IOException, InterruptedException {
        logger.info("Chater auth starting...");
        
        KafkaConsume authConsumer = new KafkaConsume();
        authConsumer.CreateConsumer("auth_requires_token", "chater-auth-group");
        
        KafkaProduce authProducer = new KafkaProduce();
        authProducer.CreateProducer();
        
        while (true) {
            try {
                String message = authConsumer.Consume();
                if (message != null && !message.isEmpty()) {
                    logger.info("Received auth request: {}", message);
                    processAuthMessage(message, authProducer);
                }
            } catch (Exception e) {
                logger.error("Error processing auth message: ", e);
                authProducer.close();
                throw new IOException("Error consuming auth message", e);
            }
        }
    }
    
    public static void processAuthMessage(String message, KafkaProduce authProducer) throws IOException, InterruptedException {
        try {
            JSONObject jsonMessage = new JSONObject(message);
            String messageKey = jsonMessage.getString("key");
            JSONObject valueObject = jsonMessage.getJSONObject("value");
            
            logger.info("Processing auth request for message key: {}", messageKey);
            
            // Process the authentication request using AuthService
            JSONObject authResponse = AuthService.processAuthRequest(valueObject);
            
            // Create response message
            JSONObject responseMessage = new JSONObject();
            responseMessage.put("key", messageKey);
            responseMessage.put("value", authResponse);
            
            // Send response back to Kafka
            authProducer.SendMessage(responseMessage.toString(), "add_auth_token");
            
            logger.info("Auth response sent for message key: {}", messageKey);
            
        } catch (Exception e) {
            logger.error("Error processing auth message: ", e);
            
            // Send error response
            try {
                JSONObject jsonMessage = new JSONObject(message);
                String messageKey = jsonMessage.getString("key");
                
                JSONObject errorResponse = new JSONObject();
                errorResponse.put("error", "processing_error");
                errorResponse.put("message", "Failed to process authentication request");
                
                JSONObject responseMessage = new JSONObject();
                responseMessage.put("key", messageKey);
                responseMessage.put("value", errorResponse);
                
                authProducer.SendMessage(responseMessage.toString(), "add_auth_token");
                
            } catch (Exception ex) {
                logger.error("Failed to send error response: ", ex);
            }
        }
    }
}
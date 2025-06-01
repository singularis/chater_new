package org.chater;

import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.Properties;
import java.util.concurrent.Future;
import org.apache.kafka.clients.producer.RecordMetadata;

public class KafkaProduce {
    private static final Logger log = LogManager.getLogger(KafkaProduce.class);
    private Producer<String, String> producer;


    public void CreateProducer() throws InterruptedException {
        log.info("Starting kafka producer...");
        String bootstrapServers = System.getenv("BOOTSTRAP_SERVERS");
        Properties properties = new Properties();
        properties.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        properties.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        properties.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        
        // Performance optimizations
        properties.setProperty(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
        properties.setProperty(ProducerConfig.BATCH_SIZE_CONFIG, "65536"); // 64KB batch
        properties.setProperty(ProducerConfig.LINGER_MS_CONFIG, "20"); // 20ms linger
        properties.setProperty(ProducerConfig.BUFFER_MEMORY_CONFIG, "134217728"); // 128MB buffer
        properties.setProperty(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
        properties.setProperty(ProducerConfig.RETRIES_CONFIG, "5");
        properties.setProperty(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, "5");
        properties.setProperty(ProducerConfig.ACKS_CONFIG, "all");
        properties.setProperty(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, "300000"); // 5 minutes
        
        this.producer = new org.apache.kafka.clients.producer.KafkaProducer<>(properties);
    }
    
    public Future<RecordMetadata> SendMessageAsync(String message, String topic) {
        log.debug("Topic: " + topic);
        log.debug("Sending message asynchronously...");
        ProducerRecord<String, String> producerRecord = new ProducerRecord<>(topic, message);
        
        // Asynchronous send with callback
        Future<RecordMetadata> future = this.producer.send(producerRecord, (metadata, exception) -> {
            if (exception != null) {
                log.error("Failed to send message: " + exception.getMessage());
            } else {
                log.debug("Message sent successfully to partition " + metadata.partition() + " with offset " + metadata.offset());
            }
        });
        
        return future;
    }
    
    public void SendMessage(String message, String topic) throws InterruptedException {
        log.info("Topic: " + topic);
        log.info("Sending message...");
        ProducerRecord<String, String> producerRecord = new ProducerRecord<>(topic, message);
        
        // Asynchronous send with callback
        this.producer.send(producerRecord, (metadata, exception) -> {
            if (exception != null) {
                log.error("Failed to send message: " + exception.getMessage());
            } else {
                log.debug("Message sent successfully to partition " + metadata.partition() + " with offset " + metadata.offset());
            }
        });
        
        // Don't flush immediately - let batching work
    }
    
    public void flush() {
        this.producer.flush();
    }
    
    public void close() {
        this.producer.close();
    }

}

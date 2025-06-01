package org.chater;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.Consumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import java.util.List;
import java.util.ArrayList;

public class KafkaConsume {
    private static final Logger log = LogManager.getLogger(KafkaConsume.class);
    private Consumer<String, String> consumer;

    public void CreateConsumer(String topic, String groupId) {
        log.info("Starting Kafka Consumer");
        String bootstrapServers = System.getenv("BOOTSTRAP_SERVERS");
        log.info("TOPIC = {}", topic);
        Properties properties = new Properties();
        properties.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        properties.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        properties.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        properties.setProperty(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        properties.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        properties.setProperty(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
        
        // Performance optimizations
        properties.setProperty(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, "1024"); // 1KB minimum
        properties.setProperty(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, "200"); // Max 200ms wait
        properties.setProperty(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, "2097152"); // 2MB per partition
        properties.setProperty(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, "30000");
        properties.setProperty(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, "10000");
        
        this.consumer = new org.apache.kafka.clients.consumer.KafkaConsumer<>(properties);
        this.consumer.subscribe(Collections.singletonList(topic));
    }
    
    public String Consume() {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000)); // Reduced poll timeout
        for (ConsumerRecord<String, String> record : records) {
            log.debug("Consumed message from partition {} with offset {}", record.partition(), record.offset());
            consumer.commitSync(); // Commit after processing
            return record.value();
        }
        return null;
    }
    
    public List<String> ConsumeBatch(int maxBatchSize) {
        List<String> messages = new ArrayList<>();
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
        
        int count = 0;
        for (ConsumerRecord<String, String> record : records) {
            log.debug("Consumed message from partition {} with offset {}", record.partition(), record.offset());
            messages.add(record.value());
            count++;
            
            if (count >= maxBatchSize) {
                break;
            }
        }
        
        if (!messages.isEmpty()) {
            consumer.commitSync(); // Batch commit
            log.debug("Consumed batch of {} messages", messages.size());
        }
        
        return messages;
    }
    
    public void close() {
        if (consumer != null) {
            consumer.close();
            log.info("Consumer closed");
        }
    }
}
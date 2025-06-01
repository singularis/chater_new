package com.chamini;

import org.apache.kafka.clients.consumer.Consumer;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.List;
import java.util.ArrayList;

public class KafkaConsumer {

    private static final Logger LOGGER = LoggerFactory.getLogger(KafkaConsumer.class);

    private final Consumer<String, String> consumer;
    private final AtomicBoolean running = new AtomicBoolean(true);

    public KafkaConsumer(String bootstrapServers, String groupId, String topic) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
        
        // Performance optimizations
        props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 1024); // 1KB minimum
        props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, 200); // Max 200ms wait
        props.put(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, 2097152); // 2MB per partition
        props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 30000);
        props.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 10000);

        this.consumer = new org.apache.kafka.clients.consumer.KafkaConsumer<>(props);
        this.consumer.subscribe(Collections.singletonList(topic));
    }

    public String consumeMessage() {
        try {
            while (running.get()) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000)); // Reduced poll timeout
                for (ConsumerRecord<String, String> record : records) {
                    LOGGER.debug("Consumed record with key {} from partition {} with offset {}", 
                        record.key(), record.partition(), record.offset());
                    // Commit after processing
                    consumer.commitSync();
                    return record.value();
                }
            }
        } catch (Exception e) {
            if (!running.get()) {
                LOGGER.info("Consumer shutdown cleanly.");
            } else {
                LOGGER.error("Error while consuming messages: {}", e.getMessage(), e);
            }
        }
        return null;
    }
    
    public List<String> consumeBatch(int maxBatchSize) {
        List<String> messages = new ArrayList<>();
        try {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
            int count = 0;
            
            for (ConsumerRecord<String, String> record : records) {
                LOGGER.debug("Consumed record with key {} from partition {} with offset {}", 
                    record.key(), record.partition(), record.offset());
                messages.add(record.value());
                count++;
                
                if (count >= maxBatchSize) {
                    break;
                }
            }
            
            if (!messages.isEmpty()) {
                consumer.commitSync(); // Batch commit
                LOGGER.debug("Consumed and committed batch of {} messages", messages.size());
            }
        } catch (Exception e) {
            LOGGER.error("Error while consuming batch: {}", e.getMessage(), e);
        }
        
        return messages;
    }

    public void close() {
        running.set(false);
        consumer.close();
        LOGGER.info("Consumer closed.");
    }
}

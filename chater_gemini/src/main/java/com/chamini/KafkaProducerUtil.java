package com.chamini;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;

public abstract class KafkaProducerUtil {

    static Logger LOGGER = LoggerFactory.getLogger(KafkaProducerUtil.class);
    private final KafkaProducer<String, String> producer;
    private final ObjectMapper objectMapper;

    public KafkaProducerUtil(String bootstrapServers) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.MAX_REQUEST_SIZE_CONFIG, 10000000);
        
        // Performance optimizations
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536); // 64KB batch
        props.put(ProducerConfig.LINGER_MS_CONFIG, 20); // 20ms linger
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 134217728); // 128MB buffer
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.RETRIES_CONFIG, 5);
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 300000); // 5 minutes

        this.producer = createProducer(props);
        this.objectMapper = new ObjectMapper();
    }

    public void sendMessage(String topic, String key, Object message) {
        try {
            JSONObject kafkaMessage = new JSONObject();
            kafkaMessage.put("key", key);
            kafkaMessage.put("value", message);
            
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, kafkaMessage.toString());
            producer.send(record, (metadata, exception) -> {
                if (exception != null) {
                    LOGGER.error("Failed to send message with key {} to topic {}: {}", key, topic, exception.getMessage());
                } else {
                    LOGGER.debug("Sent message with key {} to topic {} partition {} with offset {}", 
                        key, topic, metadata.partition(), metadata.offset());
                }
            });
            
            // Don't call flush here - let batching work
        } catch (Exception e) {
            LOGGER.error("Failed to serialize message: {}", e.getMessage());
        }
    }
    
    public void flush() {
        producer.flush();
        LOGGER.debug("Producer flushed");
    }

    public void close() {
        producer.close();
        LOGGER.info("Producer closed.");
    }

    protected abstract KafkaProducer<String, String> createProducer(Properties props);

    static class MessageWrapper {
        private String key;
        private Object value;

        public MessageWrapper(String key, Object value) {
            this.key = key;
            this.value = value;
        }

        public String getKey() {
            return key;
        }

        public void setKey(String key) {
            this.key = key;
        }

        public Object getValue() {
            return value;
        }

        public void setValue(Object value) {
            this.value = value;
        }
    }
}

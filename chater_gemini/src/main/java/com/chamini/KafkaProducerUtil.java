package com.chamini;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
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

        this.producer = new KafkaProducer<>(props);
        this.objectMapper = new ObjectMapper();
    }

    public void sendMessage(String topic, String key, Object message) {
        try {
            String jsonMessage = objectMapper.writeValueAsString(new MessageWrapper(key, message));
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, jsonMessage);
            producer.send(record, (metadata, exception) -> {
                if (exception != null) {
                    LOGGER.error("Failed to send message with key {} to topic {}: {}", key, topic, exception.getMessage());
                } else {
                    LOGGER.info("Sent message with key {} to topic {} partition {}", key, topic, metadata.partition());
                }
            });
        } catch (JsonProcessingException e) {
            LOGGER.error("Failed to serialize message: {}", e.getMessage());
        }
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

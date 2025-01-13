package org.chater;

import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.util.Properties;

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
        this.producer = new org.apache.kafka.clients.producer.KafkaProducer<>(properties);
    }
    public void SendMessage(String message, String topic) throws InterruptedException {
        log.info("Topic: " + topic);
        log.info("Sending message...");
        ProducerRecord<String, String> producerRecord = new ProducerRecord<>(topic, message);
        this.producer.send(producerRecord);
        this.producer.flush();
    }
    public void close() {

        this.producer.close();
    }

}

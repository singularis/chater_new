package com.chamini;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.slf4j.Logger;

import java.util.Properties;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.*;

class KafkaProducerUtilTest {

    private KafkaProducerUtil kafkaProducerUtil;
    private KafkaProducer<String, String> producerMock;
    private Logger loggerMock;

    @BeforeEach
    void setUp() {
        producerMock = mock(KafkaProducer.class);
        loggerMock = mock(Logger.class);

        kafkaProducerUtil = new KafkaProducerUtil("localhost:9092") {
            @Override
            protected KafkaProducer<String, String> createProducer(Properties props) {
                return producerMock;
            }
        };

        // Replace the logger in KafkaProducerUtil with our mock
        KafkaProducerUtil.LOGGER = loggerMock;
    }

    @Test
    void testSendMessageSuccess() throws JsonProcessingException, ExecutionException, InterruptedException {
        String topic = "test-topic";
        String key = "test-key";
        Object message = new Object();
        ObjectMapper objectMapper = new ObjectMapper();
        String jsonMessage = objectMapper.writeValueAsString(new KafkaProducerUtil.MessageWrapper(key, message));

        // Mocking the future and record metadata
        Future<RecordMetadata> futureMock = mock(Future.class);
        RecordMetadata metadataMock = mock(RecordMetadata.class);
        when(producerMock.send(any(ProducerRecord.class), any())).thenReturn(futureMock);
        when(futureMock.get()).thenReturn(metadataMock);
        when(metadataMock.partition()).thenReturn(1);

        kafkaProducerUtil.sendMessage(topic, key, message);

        ArgumentCaptor<ProducerRecord> recordCaptor = ArgumentCaptor.forClass(ProducerRecord.class);
        verify(producerMock).send(recordCaptor.capture(), any());
        ProducerRecord<String, String> capturedRecord = recordCaptor.getValue();

        assertEquals(topic, capturedRecord.topic());
        assertEquals(key, capturedRecord.key());
        assertEquals(jsonMessage, capturedRecord.value());

        verify(loggerMock).info("Sent message with key {} to topic {} partition {}", key, topic, metadataMock.partition());
    }

    @Test
    void testSendMessageFailure() {
        String topic = "test-topic";
        String key = "test-key";
        Object message = new Object();

        // Mocking the exception during send
        doAnswer(invocation -> {
            Object[] args = invocation.getArguments();
            ((org.apache.kafka.clients.producer.Callback) args[1]).onCompletion(null, new Exception("Kafka error"));
            return null;
        }).when(producerMock).send(any(ProducerRecord.class), any());

        kafkaProducerUtil.sendMessage(topic, key, message);

        verify(loggerMock).error("Failed to send message with key {} to topic {}: {}", key, topic, "Kafka error");
    }

    @Test
    void testSendMessageSerializationError() {
        String topic = "test-topic";
        String key = "test-key";
        Object message = new Object() {
            @Override
            public String toString() {
                throw new RuntimeException("Serialization error");
            }
        };

        kafkaProducerUtil.sendMessage(topic, key, message);

        verify(loggerMock).error("Failed to serialize message: {}", "Serialization error");
        verify(producerMock, never()).send(any(ProducerRecord.class), any());
    }

    @Test
    void testClose() {
        kafkaProducerUtil.close();
        verify(producerMock).close();
        verify(loggerMock).info("Producer closed.");
    }
}

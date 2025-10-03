package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.TrainEnqueued;
import com.config.api.ia_backend.dto.TrainRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.Objects;

@Service
@Slf4j
public class TrainingService {
    private final KafkaTemplate<String,String> kafka;
    private final String topic;
    private final ObjectMapper mapper;

    public TrainingService(KafkaTemplate<String,String> kafka, @Value("${topics.trainRequests}") String topic, ObjectMapper mapper){
        this.kafka = kafka; this.topic = topic;
        this.mapper = mapper;
    }

    public TrainEnqueued enqueue(String subjectId, TrainRequest body) {
        Objects.requireNonNull(body, "body is required");
        Objects.requireNonNull(subjectId, "subjectId is required");
        Objects.requireNonNull(topic, "topic is required");

        final String payload;
        try {
            payload = mapper.writeValueAsString(body);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("Falha ao serializar TrainRequest", e);
        }

        log.info("Payload de treinamento\n{}", payload);

        kafka.send(topic, subjectId, payload)
                .whenComplete((result, ex) -> {
                    if (ex != null) {
                        log.error("Falha ao enviar para Kafka. topic={}, key={}, msg={}",
                                topic, subjectId, ex.toString(), ex);
                    } else {
                        var md = result.getRecordMetadata();
                        log.info("Enviado ao Kafka com sucesso. topic={} partition={} offset={}",
                                md.topic(), md.partition(), md.offset());
                    }
                });

        return new TrainEnqueued(subjectId, "QUEUED");
    }

}


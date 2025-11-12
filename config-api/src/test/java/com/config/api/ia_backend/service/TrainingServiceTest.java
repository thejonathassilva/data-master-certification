package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.TrainEnqueued;
import com.config.api.ia_backend.dto.TrainRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.kafka.core.KafkaTemplate;

import java.util.concurrent.CompletableFuture;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

class TrainingServiceTest {

    @Test
    void enqueue_ok() throws JsonProcessingException {
        @SuppressWarnings("unchecked")
        KafkaTemplate<String, String> kafka = mock(KafkaTemplate.class);

        // devolve um Future NÃO-NULO, já completo com exceção (simulando falha no envio)
        when(kafka.send(anyString(), anyString(), anyString()))
                .thenReturn(CompletableFuture.failedFuture(new RuntimeException("boom")));

        var svc = new TrainingService(kafka, "train.requests", new ObjectMapper());

        TrainEnqueued out = svc.enqueue(
                "subj1",
                new TrainRequest(
                        "both",
                        "689cbe4dd31779621d1a1d58",
                        "PF",
                        "auto",
                        null,
                        "pt_core_news_md",
                        "console",
                        "exemplos_atualizados",
                        "00000000-0000-0000-0000-000000000000"
                )
        );

        assertEquals("subj1", out.subjectId());
    }
}


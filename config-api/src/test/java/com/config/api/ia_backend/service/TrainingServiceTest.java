package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.TrainEnqueued;
import com.config.api.ia_backend.dto.TrainRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.kafka.core.KafkaTemplate;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

public class TrainingServiceTest {
    @Test
    void enqueue_ok() throws JsonProcessingException {
        var kafka = mock(KafkaTemplate.class);
        when(kafka.send(anyString(), anyString(), anyString())).thenReturn(null);
        var svc = new TrainingService(kafka, "train.requests", mock(ObjectMapper.class));
        TrainEnqueued out = svc.enqueue("subj1", new TrainRequest("both",
                "689cbe4dd31779621d1a1d58", "PF", "auto", null,
                "pt_core_news_md", "console", "exemplos_atualizados",
                "00000000-0000-0000-0000-000000000000"));
        assertEquals("subj1", out.subjectId());
    }
}


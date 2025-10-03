package com.config.api.ia_backend.service;

import com.config.api.ia_backend.client.JAssistantPredictClient;
import com.config.api.ia_backend.client.PredictApiClient;
import com.config.api.ia_backend.dto.PredictRequest;
import com.config.api.ia_backend.dto.PredictionResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class JAssistantPredictionService {

    private final JAssistantPredictClient client;
    private final DialogNodeService dialog;
    private final ObjectMapper mapper;

    public JAssistantPredictionService(JAssistantPredictClient client,
                                       DialogNodeService dialog,
                                       ObjectMapper mapper) {
        this.client = client;
        this.dialog = dialog;
        this.mapper = mapper;
    }

    public PredictionResponse predict(String channel, PredictRequest req) {
        log.info("[predict] channel={} req={}", channel, toJson(req));

        var subject = client.predict(channel, req);
        log.info("[subject] subjectId={} subject={}",
                subject.subjectId(), toJson(subject));

        var node = dialog.resolveJAssistant(subject.subjectId(), subject.intentName(), subject.confidence());
        log.info("[dialog.resolve] toJson: {}", toJson(node));

        return new PredictionResponse(subject.subjectId(), subject.intentName(), subject.confidence(), null, node);
    }

    private String toJson(Object o) {
        try {
            return mapper.writeValueAsString(o);
        } catch (Exception e) {
            return String.valueOf(o);
        }
    }
}

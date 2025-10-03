package com.config.api.ia_backend.service;

import com.config.api.ia_backend.client.PredictApiClient;
import com.config.api.ia_backend.dto.PredictRequest;
import com.config.api.ia_backend.dto.PredictionResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.function.Supplier;

@Service
@Slf4j
public class PredictionService {
    private final PredictApiClient client;
    private final ThresholdService thresholds;
    private final DialogNodeService dialog;
    private final ObjectMapper mapper;

    public PredictionService(PredictApiClient client, ThresholdService thresholds, DialogNodeService dialog, ObjectMapper mapper){
        this.client = client; this.thresholds = thresholds; this.dialog = dialog;
        this.mapper = mapper;
    }

    public PredictionResponse predict(String channel, PredictRequest req){
        log.info("[predict] channel={} req={}", channel, toJson(req));

        var subject = client.predictSubject(channel, req);
        log.info("[subject] subjectId={} raw={}",
                subject.subjectId(), toJson(subject));

        var intent = client.predictIntentNer(subject.subjectId(), req);
        log.info("[intent] subjectId={} intentId={} confidence={} entities={} raw={}",
                subject.subjectId(),
                safe(() -> intent.intentId()),
                safe(() -> intent.confidence()),
                safe(() -> intent.entities()),
                toJson(intent));

        var applied = thresholds.apply(subject.subjectId(), intent);
        log.info("[thresholds.apply] subjectId={} chosenIntentId={} finalConfidence={} minThreshold={} rejectedByMin?={} raw={}",
                subject.subjectId(),
                safe(() -> applied.intentId()),
                safe(() -> applied.confidence()),
                toJson(applied.entities()));

        var node = dialog.resolve(subject.subjectId(), applied.intentId(), applied.confidence());
        log.info("[dialog.resolve] toJson: {}", toJson(node));

        return new PredictionResponse(subject.subjectId(), applied.intentId(), applied.confidence(), applied.entities(), node);
    }

    private String toJson(Object o) {
        try {
            return mapper.writeValueAsString(o);
        } catch (Exception e) {
            return String.valueOf(o);
        }
    }

    private String shorten(Object val, int max) {
        if (val == null) return null;
        String s = String.valueOf(val);
        return s.length() <= max ? s : s.substring(0, max) + "...";
    }

    private <T> T safe(Supplier<T> s) {
        try { return s.get(); } catch (Exception e) { return null; }
    }
}

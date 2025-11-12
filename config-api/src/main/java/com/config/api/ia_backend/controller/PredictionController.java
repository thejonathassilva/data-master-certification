package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.PredictRequest;
import com.config.api.ia_backend.dto.PredictionResponse;
import com.config.api.ia_backend.service.JAssistantPredictionService;
import com.config.api.ia_backend.service.PredictionService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController @RequestMapping("/api")
@AllArgsConstructor
@Slf4j
public class PredictionController {
    private final PredictionService predictionService;
    private final JAssistantPredictionService jAssistantService;

    @PostMapping("/predict")
    @CircuitBreaker(name = "predictService", fallbackMethod = "predictFallback")
    public PredictionResponse predict(@RequestParam String channel,
                                      @Valid @RequestBody PredictRequest req,
                                      @RequestHeader(value = "IA", required = false) String ia ){
        UUID uuid = UUID.randomUUID();
        if ("J_assistant".equalsIgnoreCase(ia)) {
            var res = jAssistantService.predict(channel, req);
            log.info("[FINAL-ANSWER] REQ={} | CANAL={} | UUID={} | RESPOSTA={} | INTENT={} | CONFIDENCE={} | IA={}",
                    req.text(), channel, uuid, res.node(), res.intentId(), res.confidence(), ia);

            return res;
        }
        var res = predictionService.predict(channel, req);
        log.info("[FINAL-ANSWER] REQ={} | CANAL={} | UUID={} | RESPOSTA={} | INTENT={} | CONFIDENCE={} | IA={}",
                req.text(), channel, uuid, res.node(), res.intentId(), res.confidence(), ia);
        return res;
    }

    @PostMapping("/simulate")
    public PredictionResponse simulate(@RequestParam String channel, @Valid @RequestBody PredictRequest req){
        return predictionService.predict(channel, req);
    }

    private PredictionResponse predictFallback(String channel,
                                               PredictRequest req,
                                               String ia,
                                               Throwable t,
                                               String uuid) {
        var res = jAssistantService.predict(channel, req);
        log.info("[FINAL-ANSWER] REQ={} | CANAL={} | UUID={} | RESPOSTA={} | INTENT={} | CONFIDENCE={} | IA={}",
                req.text(), channel, uuid, res.node(), res.intentId(), res.confidence(), ia);
        return res;
    }
}


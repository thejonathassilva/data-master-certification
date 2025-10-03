package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.PredictRequest;
import com.config.api.ia_backend.dto.PredictionResponse;
import com.config.api.ia_backend.service.JAssistantPredictionService;
import com.config.api.ia_backend.service.PredictionService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api")
@AllArgsConstructor
public class PredictionController {
    private final PredictionService predictionService;
    private final JAssistantPredictionService jAssistantService;

    @PostMapping("/predict")
    public PredictionResponse predict(@RequestParam String channel,
                                      @Valid @RequestBody PredictRequest req,
                                      @RequestHeader(value = "IA", required = false) String ia ){
        if ("J_assistant".equalsIgnoreCase(ia)) {
            return jAssistantService.predict(channel, req);
        }
        return predictionService.predict(channel, req);
    }

    @PostMapping("/simulate")
    public PredictionResponse simulate(@RequestParam String channel, @Valid @RequestBody PredictRequest req){
        return predictionService.predict(channel, req);
    }
}


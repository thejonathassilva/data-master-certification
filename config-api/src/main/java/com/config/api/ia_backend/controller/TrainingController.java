package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.TrainEnqueued;
import com.config.api.ia_backend.dto.TrainRequest;
import com.config.api.ia_backend.service.TrainingService;
import com.fasterxml.jackson.core.JsonProcessingException;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api")
@AllArgsConstructor
public class TrainingController {
    private final TrainingService service;

    @PostMapping("/subjects/{id}/train")
    public TrainEnqueued train(@PathVariable("id") String subjectId,
                               @RequestBody(required=false) @Valid TrainRequest req) throws JsonProcessingException {
        TrainRequest fixedReq = new TrainRequest(
                req.scope(),
                subjectId,
                req.channel(),
                req.versioning_strategy(),
                req.base_version(),
                req.base_lang_model(),
                req.requested_by() != null ? req.requested_by() : "console",
                req.notes(),
                req.correlation_id()
        );
        return service.enqueue(subjectId, fixedReq);
    }
}


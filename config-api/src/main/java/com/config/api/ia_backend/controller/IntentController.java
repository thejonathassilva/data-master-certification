package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.intent.IntentCreateRequest;
import com.config.api.ia_backend.dto.intent.IntentResponse;
import com.config.api.ia_backend.dto.intent.IntentUpdateRequest;
import com.config.api.ia_backend.service.IntentService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController @RequestMapping("/api/intents")
@AllArgsConstructor
public class IntentController {
    private final IntentService intentService;

    @PostMapping
    public IntentResponse create(@Valid @RequestBody IntentCreateRequest request) {
        return intentService.create(request);
    }

    @GetMapping("/{id}")
    public IntentResponse get(@PathVariable String id) {
        return intentService.get(id);
    }

    @GetMapping
    public List<IntentResponse> list(@RequestParam(required=false) String subjectId) {
        return intentService.list(subjectId);
    }

    @PutMapping("/{id}")
    public IntentResponse update(@PathVariable String id, @RequestBody IntentUpdateRequest request) {
        return intentService.update(id, request);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) {
        intentService.delete(id);
    }
}


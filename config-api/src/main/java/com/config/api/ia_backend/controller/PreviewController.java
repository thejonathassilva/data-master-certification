package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.PreviewRequest;
import com.config.api.ia_backend.dto.PreviewResponse;
import com.config.api.ia_backend.service.PreviewService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api")
@AllArgsConstructor
public class PreviewController {
    private final PreviewService previewService;

    @PostMapping("/preview/intent")
    public PreviewResponse preview(@Valid @RequestBody PreviewRequest req){
        return previewService.preview(req);
    }
}


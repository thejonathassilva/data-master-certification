package com.config.api.ia_backend.dto.entities;

import jakarta.validation.constraints.NotBlank;

import java.util.List;

public record EntityCreateRequest(
        @NotBlank String subjectId,
        @NotBlank String name,
        List<String> patterns,
        List<String> gazetteer
) {}

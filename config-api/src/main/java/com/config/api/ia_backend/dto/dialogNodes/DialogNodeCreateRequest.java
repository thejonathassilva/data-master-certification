package com.config.api.ia_backend.dto.dialogNodes;

import jakarta.validation.constraints.NotBlank;

import java.util.List;

public record DialogNodeCreateRequest(
        @NotBlank String subjectId,
        @NotBlank String name,
        String conditionType,  // "intent" | "expr" | "true"
        String conditionValue,
        String responseText,
        List<String> responseActions,
        List<String> children
) {}

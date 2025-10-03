package com.config.api.ia_backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record TrainRequest(
        @NotBlank String scope,
        @NotBlank String subject_id,
        String channel,
        @NotBlank String versioning_strategy,
        String base_version,
        String base_lang_model,
        String requested_by,
        String notes,
        @NotBlank String correlation_id
) {}


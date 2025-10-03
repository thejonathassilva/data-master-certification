package com.config.api.ia_backend.dto.intent;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public record IntentCreateRequest(
        @NotBlank String subjectId,
        @NotBlank String name,
        @NotNull List<String> examples,
        Boolean active
) {}

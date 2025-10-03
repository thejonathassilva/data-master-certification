package com.config.api.ia_backend.dto;

import jakarta.validation.constraints.NotBlank;

public record PredictRequest(@NotBlank String text) {}

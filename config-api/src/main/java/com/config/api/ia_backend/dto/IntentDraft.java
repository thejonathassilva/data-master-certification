package com.config.api.ia_backend.dto;

import jakarta.validation.constraints.NotBlank;

import java.util.List;

public record IntentDraft(@NotBlank String name, List<String> examples) {}

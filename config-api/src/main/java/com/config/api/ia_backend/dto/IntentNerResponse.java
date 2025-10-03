package com.config.api.ia_backend.dto;

import java.util.List;

public record IntentNerResponse(String intentId, double confidence, List<EntityDTO> entities) {}

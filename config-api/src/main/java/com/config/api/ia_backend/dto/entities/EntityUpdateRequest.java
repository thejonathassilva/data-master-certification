package com.config.api.ia_backend.dto.entities;

import java.util.List;

public record EntityUpdateRequest(
        String name,
        List<String> patterns,
        List<String> gazetteer
) {}

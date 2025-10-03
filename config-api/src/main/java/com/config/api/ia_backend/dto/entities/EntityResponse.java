package com.config.api.ia_backend.dto.entities;

import java.util.List;

public record EntityResponse(
        String id, String subjectId, String name, List<String> patterns, List<String> gazetteer
) {}
package com.config.api.ia_backend.dto;

import java.util.Map;

public record SubjectClassifyResponse(String subjectId, Map<String, Double> scores) {}

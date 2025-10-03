package com.config.api.ia_backend.dto;

import java.util.List;
import java.util.Map;

public record PreviewResponse(java.util.Map<String,Double> deltaMetrics,
                              List<Map<String,Object>> sampleConfidence,
                              List<List<Object>> topConfusions) {}

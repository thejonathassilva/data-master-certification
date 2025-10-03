package com.config.api.ia_backend.dto;

import java.util.List;

public record PredictionResponse(String subjectId,String intentId,double confidence,List<EntityDTO> entities,Object node) {}


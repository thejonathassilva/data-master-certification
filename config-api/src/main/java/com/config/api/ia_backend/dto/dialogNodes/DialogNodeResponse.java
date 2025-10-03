package com.config.api.ia_backend.dto.dialogNodes;

import java.util.List;

public record DialogNodeResponse(
        String id, String subjectId, String name,
        String conditionType, String conditionValue,
        String responseText, List<String> responseActions,
        List<String> children
) {}

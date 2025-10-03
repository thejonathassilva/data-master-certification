package com.config.api.ia_backend.dto.intent;

import java.util.List;

public record IntentResponse(
        String id, String subjectId, String name, List<String> examples, boolean active
) {}

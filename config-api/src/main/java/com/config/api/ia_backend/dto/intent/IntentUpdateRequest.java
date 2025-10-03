package com.config.api.ia_backend.dto.intent;

import java.util.List;

public record IntentUpdateRequest(
        String name,
        List<String> examples,
        Boolean active
) {}

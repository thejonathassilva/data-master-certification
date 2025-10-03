package com.config.api.ia_backend.dto.subject;

public record SubjectUpdateRequest(
        String name,
        Double intentMinConf,
        Double entityMinConf,
        String activeModelVersion
) {}

package com.config.api.ia_backend.dto.subject;

public record SubjectResponse(
        String id, String channelId, String name,
        String activeModelVersion,
        Double intentMinConf, Double entityMinConf
) {}

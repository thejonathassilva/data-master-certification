package com.config.api.ia_backend.dto.subject;

import jakarta.validation.constraints.NotBlank;

public record SubjectCreateRequest(
        @NotBlank String channelId,
        @NotBlank String name,
        Double intentMinConf,
        Double entityMinConf
) {}

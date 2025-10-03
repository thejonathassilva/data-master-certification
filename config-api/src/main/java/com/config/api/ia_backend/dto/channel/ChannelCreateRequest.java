package com.config.api.ia_backend.dto.channel;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ChannelCreateRequest(
        @NotBlank String name,
        @NotNull Double minConfSubject
) {}

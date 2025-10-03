package com.config.api.ia_backend.dto.channel;

public record ChannelUpdateRequest(
        String name,
        Double minConfSubject
) {}


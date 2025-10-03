package com.config.api.ia_backend.dto;

public record JAssistantResponse(
        @com.fasterxml.jackson.annotation.JsonProperty("subjectId") String subjectId,
        @com.fasterxml.jackson.annotation.JsonProperty("intentName") String intentName,
        @com.fasterxml.jackson.annotation.JsonProperty("confidence") Double confidence
) {}

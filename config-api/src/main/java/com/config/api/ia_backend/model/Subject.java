package com.config.api.ia_backend.model;

import lombok.*;
import org.springframework.data.annotation.*;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document("subjects")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Subject {
    @Id private String id;

    private String channelId;
    private String name;
    private String activeModelVersion;

    private Thresholds thresholds;

    @CreatedDate private Instant createdAt;
    @LastModifiedDate private Instant updatedAt;

    @Data @NoArgsConstructor @AllArgsConstructor
    public static class Thresholds {
        private Double intentMinConf;
        private Double entityMinConf;
    }
}


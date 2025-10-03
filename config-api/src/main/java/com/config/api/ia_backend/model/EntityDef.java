package com.config.api.ia_backend.model;

import lombok.*;
import org.springframework.data.annotation.*;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.List;

@Document("entities")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class EntityDef {
    @Id private String id;

    private String subjectId;
    private String name;
    private List<String> patterns;
    private List<String> gazetteer;

    @CreatedDate private Instant createdAt;
    @LastModifiedDate private Instant updatedAt;
}


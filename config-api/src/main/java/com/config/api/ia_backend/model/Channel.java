package com.config.api.ia_backend.model;

import lombok.*;
import org.springframework.data.annotation.*;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document("channels")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Channel {
    @Id private String id;

    @Indexed(unique = true)
    private String name;
    private Double minConfSubject;

    @CreatedDate private Instant createdAt;
    @LastModifiedDate private Instant updatedAt;
}


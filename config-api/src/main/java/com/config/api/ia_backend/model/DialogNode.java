package com.config.api.ia_backend.model;

import lombok.*;
import org.springframework.data.annotation.*;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.List;

@Document("dialog_nodes")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class DialogNode {
    @Id private String id;

    private String subjectId;
    private String name;

    private Condition condition;
    private Response response;
    private List<String> children;

    @CreatedDate private Instant createdAt;
    @LastModifiedDate private Instant updatedAt;

    @Data @NoArgsConstructor @AllArgsConstructor
    public static class Condition {
        private String type;
        private String value;
    }

    @Data @NoArgsConstructor @AllArgsConstructor
    public static class Response {
        private String text;
        private List<String> actions;
    }
}


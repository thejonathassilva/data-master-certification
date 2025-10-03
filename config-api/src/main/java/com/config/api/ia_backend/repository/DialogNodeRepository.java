package com.config.api.ia_backend.repository;

import com.config.api.ia_backend.model.DialogNode;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface DialogNodeRepository extends MongoRepository<DialogNode, String> {
    List<DialogNode> findBySubjectId(String subjectId);
}


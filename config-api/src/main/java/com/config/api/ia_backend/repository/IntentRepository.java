package com.config.api.ia_backend.repository;
import com.config.api.ia_backend.model.IntentDef;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface IntentRepository extends MongoRepository<IntentDef, String> {
    List<IntentDef> findBySubjectId(String subjectId);
    IntentDef findFirstByName(String name);
}


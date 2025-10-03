package com.config.api.ia_backend.repository;
import com.config.api.ia_backend.model.EntityDef;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface EntityRepository extends MongoRepository<EntityDef, String> {
    List<EntityDef> findBySubjectId(String subjectId);
}


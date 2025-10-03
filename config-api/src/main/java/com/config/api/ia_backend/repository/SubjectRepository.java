package com.config.api.ia_backend.repository;

import com.config.api.ia_backend.model.Subject;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface SubjectRepository extends MongoRepository<Subject, String> {
    List<Subject> findByChannelId(String channelId);
    Subject findByName(String subjectName);
}

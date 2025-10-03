package com.config.api.ia_backend.service;

import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.SubjectRepository;
import org.springframework.stereotype.Service;

@Service
public class VersioningService {
    private final SubjectRepository subjects;
    public VersioningService(SubjectRepository subjects){ this.subjects = subjects; }

    public String resolveActiveIntentModel(String subjectId){
        Subject subject = subjects.findById(subjectId).orElseThrow();
        return subject.getActiveModelVersion();
    }
}

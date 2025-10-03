package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.IntentNerResponse;
import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.SubjectRepository;
import org.springframework.stereotype.Service;

@Service
public class ThresholdService {
    private final SubjectRepository subjects;
    public ThresholdService(SubjectRepository subjects){ this.subjects = subjects; }

    public IntentNerResponse apply(String subjectId, IntentNerResponse resp){
        Subject subject = subjects.findByName(subjectId);
        Double min = subject.getThresholds()!=null ? subject.getThresholds().getIntentMinConf() : 0.0;
        if (min!=null && resp.confidence()<min) {
            return new IntentNerResponse("LOW_CONFIDENCE", resp.confidence(), resp.entities());
        }
        return resp;
    }
}

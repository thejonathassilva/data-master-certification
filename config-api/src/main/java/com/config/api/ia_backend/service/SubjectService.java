package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.subject.SubjectCreateRequest;
import com.config.api.ia_backend.dto.subject.SubjectResponse;
import com.config.api.ia_backend.dto.subject.SubjectUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.ChannelRepository;
import com.config.api.ia_backend.repository.SubjectRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor
public class SubjectService {
    private final SubjectRepository subjectRepository;
    private final ChannelRepository channelRepository;

    public SubjectResponse create(SubjectCreateRequest request){
        channelRepository.findById(request.channelId()).orElseThrow(() -> new BadRequestException("channelId inválido"));
        var th = new Subject.Thresholds(request.intentMinConf(), request.entityMinConf());
        Subject subject = subjectRepository.save(Subject.builder()
                .channelId(request.channelId())
                .name(request.name())
                .thresholds(th)
                .build());
        return map(subject);
    }

    public SubjectResponse get(String id){
        return map(subjectRepository.findById(id).orElseThrow(() -> new NotFoundException("Subject not found")));
    }

    public List<SubjectResponse> list(String channelId){
        var list = (channelId==null) ? subjectRepository.findAll() : subjectRepository.findByChannelId(channelId);
        return list.stream().map(this::map).toList();
    }

    public SubjectResponse update(String id, SubjectUpdateRequest subjectUpdateRequest){
        Subject subject = subjectRepository.findById(id).orElseThrow(() -> new NotFoundException("Subject not found"));
        if (subjectUpdateRequest.name()!=null) subject.setName(subjectUpdateRequest.name());
        if (subjectUpdateRequest.intentMinConf()!=null || subjectUpdateRequest.entityMinConf()!=null){
            var th = (subject.getThresholds()==null) ? new Subject.Thresholds(null,null) : subject.getThresholds();
            if (subjectUpdateRequest.intentMinConf()!=null) th.setIntentMinConf(subjectUpdateRequest.intentMinConf());
            if (subjectUpdateRequest.entityMinConf()!=null) th.setEntityMinConf(subjectUpdateRequest.entityMinConf());
            subject.setThresholds(th);
        }
        if (subjectUpdateRequest.activeModelVersion()!=null) subject.setActiveModelVersion(subjectUpdateRequest.activeModelVersion());
        return map(subjectRepository.save(subject));
    }

    public void delete(String id){
        if (!subjectRepository.existsById(id)) throw new NotFoundException("Subject not found");
        subjectRepository.deleteById(id);
    }

    private SubjectResponse map(Subject subject){
        Double i = subject.getThresholds()!=null ? subject.getThresholds().getIntentMinConf() : null;
        Double e = subject.getThresholds()!=null ? subject.getThresholds().getEntityMinConf() : null;
        return new SubjectResponse(subject.getId(), subject.getChannelId(), subject.getName(), subject.getActiveModelVersion(), i, e);
    }
}


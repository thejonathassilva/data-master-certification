package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.intent.IntentCreateRequest;
import com.config.api.ia_backend.dto.intent.IntentResponse;
import com.config.api.ia_backend.dto.intent.IntentUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.IntentDef;
import com.config.api.ia_backend.repository.IntentRepository;
import com.config.api.ia_backend.repository.SubjectRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor
public class IntentService {
    private final IntentRepository intentRepository;
    private final SubjectRepository subjectRepository;


    public IntentResponse create(IntentCreateRequest request) {
        subjectRepository.findById(request.subjectId())
                .orElseThrow(() -> new BadRequestException("subjectId inválido"));

        if (intentRepository.findFirstByName(request.name()) != null) {
            throw new BadRequestException("Já existe uma intent com este nome");
        }

        IntentDef intent = intentRepository.save(IntentDef.builder()
                .subjectId(request.subjectId())
                .name(request.name())
                .examples(request.examples())
                .active(Boolean.TRUE.equals(request.active()))
                .build());

        return map(intent);
    }

    public IntentResponse get(String id){
        return map(intentRepository.findById(id).orElseThrow(() -> new NotFoundException("Intent not found")));
    }

    public List<IntentResponse> list(String subjectId){
        var list = (subjectId==null) ? intentRepository.findAll() : intentRepository.findBySubjectId(subjectId);
        return list.stream().map(this::map).toList();
    }

    public IntentResponse update(String id, IntentUpdateRequest request){
        IntentDef intent = intentRepository.findById(id).orElseThrow(() -> new NotFoundException("Intent not found"));
        if (request.name()!=null) intent.setName(request.name());
        if (request.examples()!=null) intent.setExamples(request.examples());
        if (request.active()!=null) intent.setActive(request.active());
        return map(intentRepository.save(intent));
    }

    public void delete(String id){
        if (!intentRepository.existsById(id)) throw new NotFoundException("Intent not found");
        intentRepository.deleteById(id);
    }

    private IntentResponse map(IntentDef intent){
        return new IntentResponse(intent.getId(), intent.getSubjectId(), intent.getName(), intent.getExamples(), intent.isActive());
    }
}


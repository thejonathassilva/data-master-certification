package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.entities.EntityCreateRequest;
import com.config.api.ia_backend.dto.entities.EntityResponse;
import com.config.api.ia_backend.dto.entities.EntityUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.EntityDef;
import com.config.api.ia_backend.repository.EntityRepository;
import com.config.api.ia_backend.repository.SubjectRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor
public class EntityService {
    private final EntityRepository entityRepository;
    private final SubjectRepository subjectRepository;


    public EntityResponse create(EntityCreateRequest request){
        subjectRepository.findById(request.subjectId()).orElseThrow(() -> new BadRequestException("subjectId inválido"));
        EntityDef entity = entityRepository.save(EntityDef.builder()
                .subjectId(request.subjectId())
                .name(request.name())
                .patterns(request.patterns())
                .gazetteer(request.gazetteer())
                .build());
        return map(entity);
    }

    public EntityResponse get(String id){
        return map(entityRepository.findById(id).orElseThrow(() -> new NotFoundException("Entity not found")));
    }

    public List<EntityResponse> list(String subjectId){
        var list = (subjectId==null) ? entityRepository.findAll() : entityRepository.findBySubjectId(subjectId);
        return list.stream().map(this::map).toList();
    }

    public EntityResponse update(String id, EntityUpdateRequest request){
        EntityDef entity = entityRepository.findById(id).orElseThrow(() -> new NotFoundException("Entity not found"));
        if (request.name()!=null) entity.setName(request.name());
        if (request.patterns()!=null) entity.setPatterns(request.patterns());
        if (request.gazetteer()!=null) entity.setGazetteer(request.gazetteer());
        return map(entityRepository.save(entity));
    }

    public void delete(String id){
        if (!entityRepository.existsById(id)) throw new NotFoundException("Entity not found");
        entityRepository.deleteById(id);
    }

    private EntityResponse map(EntityDef entity){
        return new EntityResponse(entity.getId(), entity.getSubjectId(), entity.getName(), entity.getPatterns(), entity.getGazetteer());
    }
}


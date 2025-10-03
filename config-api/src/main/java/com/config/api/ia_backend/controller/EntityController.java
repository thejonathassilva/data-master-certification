package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.entities.EntityCreateRequest;
import com.config.api.ia_backend.dto.entities.EntityResponse;
import com.config.api.ia_backend.dto.entities.EntityUpdateRequest;
import com.config.api.ia_backend.service.EntityService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController @RequestMapping("/api/entities")
@AllArgsConstructor
public class EntityController {
    private final EntityService entityService;

    @PostMapping
    public EntityResponse create(@Valid @RequestBody EntityCreateRequest request) {
        return entityService.create(request);
    }

    @GetMapping("/{id}")
    public EntityResponse get(@PathVariable String id) {
        return entityService.get(id);
    }

    @GetMapping
    public List<EntityResponse> list(@RequestParam(required=false) String subjectId) {
        return entityService.list(subjectId);
    }

    @PutMapping("/{id}")
    public EntityResponse update(@PathVariable String id, @RequestBody EntityUpdateRequest request) {
        return entityService.update(id, request);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) {
        entityService.delete(id);
    }
}


package com.config.api.ia_backend.controller;


import com.config.api.ia_backend.dto.subject.SubjectCreateRequest;
import com.config.api.ia_backend.dto.subject.SubjectResponse;
import com.config.api.ia_backend.dto.subject.SubjectUpdateRequest;
import com.config.api.ia_backend.service.SubjectService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController @RequestMapping("/api/subjects")
@AllArgsConstructor
public class SubjectController {
    private final SubjectService subjectService;

    @PostMapping
    public SubjectResponse create(@Valid @RequestBody SubjectCreateRequest request) {
        return subjectService.create(request);
    }

    @GetMapping("/{id}")
    public SubjectResponse get(@PathVariable String id){
        return subjectService.get(id);
    }

    @GetMapping
    public List<SubjectResponse> list(@RequestParam(required=false) String channelId){
        return subjectService.list(channelId);
    }

    @PutMapping("/{id}")
    public SubjectResponse update(@PathVariable String id, @RequestBody SubjectUpdateRequest request){
        return subjectService.update(id, request);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id){
        subjectService.delete(id);
    }
}


package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.dialogNodes.DialogNodeCreateRequest;
import com.config.api.ia_backend.dto.dialogNodes.DialogNodeResponse;
import com.config.api.ia_backend.dto.dialogNodes.DialogNodeUpdateRequest;
import com.config.api.ia_backend.service.DialogNodeService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController @RequestMapping("/api/dialog-nodes")
@AllArgsConstructor
public class DialogNodeController {
    private final DialogNodeService dialogNodeService;

    @PostMapping
    public DialogNodeResponse create(@Valid @RequestBody DialogNodeCreateRequest request) {
        return dialogNodeService.create(request);
    }

    @GetMapping("/{id}")
    public DialogNodeResponse get(@PathVariable String id) {
        return dialogNodeService.get(id);
    }

    @GetMapping
    public List<DialogNodeResponse> list(@RequestParam(required=false) String subjectId) {
        return dialogNodeService.list(subjectId);
    }

    @PutMapping("/{id}")
    public DialogNodeResponse update(@PathVariable String id, @RequestBody DialogNodeUpdateRequest request) {
        return dialogNodeService.update(id, request);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) {
        dialogNodeService.delete(id);
    }
}


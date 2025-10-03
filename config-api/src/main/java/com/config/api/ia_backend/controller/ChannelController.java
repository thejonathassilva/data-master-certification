package com.config.api.ia_backend.controller;

import com.config.api.ia_backend.dto.channel.ChannelCreateRequest;
import com.config.api.ia_backend.dto.channel.ChannelResponse;
import com.config.api.ia_backend.dto.channel.ChannelUpdateRequest;
import com.config.api.ia_backend.service.ChannelService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController @RequestMapping("/api/channels")
@AllArgsConstructor
public class ChannelController {
    private final ChannelService channelService;

    @PostMapping
    public ChannelResponse create(@Valid @RequestBody ChannelCreateRequest request) {
        return channelService.create(request);
    }

    @GetMapping("/{id}")
    public ChannelResponse get(@PathVariable String id) {
        return channelService.get(id);
    }

    @GetMapping
    public List<ChannelResponse> list() {
        return channelService.list();
    }

    @PutMapping("/{id}")
    public ChannelResponse update(@PathVariable String id, @RequestBody ChannelUpdateRequest request) {
        return channelService.update(id, request);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) {
        channelService.delete(id);
    }
}


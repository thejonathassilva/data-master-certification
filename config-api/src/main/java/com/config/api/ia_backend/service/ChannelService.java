package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.channel.ChannelCreateRequest;
import com.config.api.ia_backend.dto.channel.ChannelResponse;
import com.config.api.ia_backend.dto.channel.ChannelUpdateRequest;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.Channel;
import com.config.api.ia_backend.repository.ChannelRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor
public class ChannelService {
    private final ChannelRepository channelRepository;

    public ChannelResponse create(ChannelCreateRequest r){
        Channel channel = channelRepository.save(Channel.builder()
                .name(r.name())
                .minConfSubject(r.minConfSubject())
                .build());
        return map(channel);
    }

    public ChannelResponse get(String id){
        return map(channelRepository.findById(id).orElseThrow(() -> new NotFoundException("Channel not found")));
    }

    public List<ChannelResponse> list(){
        return channelRepository.findAll().stream().map(this::map).toList();
    }

    public ChannelResponse update(String id, ChannelUpdateRequest r){
        Channel channel = channelRepository.findById(id).orElseThrow(() -> new NotFoundException("Channel not found"));
        if (r.name()!=null) channel.setName(r.name());
        if (r.minConfSubject()!=null) channel.setMinConfSubject(r.minConfSubject());
        return map(channelRepository.save(channel));
    }

    public void delete(String id){
        if (!channelRepository.existsById(id)) throw new NotFoundException("Channel not found");
        channelRepository.deleteById(id);
    }

    private ChannelResponse map(Channel channel){
        return new ChannelResponse(channel.getId(), channel.getName(), channel.getMinConfSubject());
    }
}


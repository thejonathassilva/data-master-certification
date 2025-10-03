package com.config.api.ia_backend.repository;

import com.config.api.ia_backend.model.Channel;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface ChannelRepository extends MongoRepository<Channel, String> {
    Optional<Channel> findByName(String name);
}


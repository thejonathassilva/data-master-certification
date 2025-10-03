package com.config.api.ia_backend.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class KafkaConfig {
    @Bean
    NewTopic trainRequests(@Value("${topics.trainRequests}") String name) {
        return new NewTopic(name, 1, (short)1);
    }
    @Bean
    NewTopic trainStatus(@Value("${topics.trainStatus}") String name) {
        return new NewTopic(name, 1, (short)1);
    }
}


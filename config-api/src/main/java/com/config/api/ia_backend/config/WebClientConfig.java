package com.config.api.ia_backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {
    @Bean("predictWebClient")
    @Primary
    WebClient predictWebClient(@Value("${predict.base-url}") String baseUrl) {
        return WebClient.builder().baseUrl(baseUrl).build();
    }

    @Bean("jAssistantWebClient")
    WebClient predictJAssistantWebClient(@Value("${j-assistant.base-url}") String baseUrl) {
        return WebClient.builder().baseUrl(baseUrl).build();
    }
}


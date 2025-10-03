package com.config.api.ia_backend.client;

import com.config.api.ia_backend.dto.JAssistantResponse;
import com.config.api.ia_backend.dto.PredictRequest;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@Slf4j
public class JAssistantPredictClient {
    private final WebClient web;

    public JAssistantPredictClient(@Qualifier("jAssistantWebClient") WebClient web) {
        this.web = web;
    }

    public JAssistantResponse predict(String channel, PredictRequest body) {
        return web.post()
                .uri(uri -> uri.path("/predict").queryParam("channel", channel).build())
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(body)
                .retrieve()
                .bodyToMono(JAssistantResponse.class)
                .block();
    }
}

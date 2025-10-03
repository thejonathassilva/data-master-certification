package com.config.api.ia_backend.client;

import com.config.api.ia_backend.dto.*;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@AllArgsConstructor
@Slf4j
public class PredictApiClient {
    private final WebClient web;

    public SubjectClassifyResponse predictSubject(String channel, PredictRequest body) {
        return web.post().uri(uri -> uri.path("/predict/subject").queryParam("channel", channel).build())
                .bodyValue(body).retrieve().bodyToMono(SubjectClassifyResponse.class).block();
    }

    public IntentNerResponse predictIntentNer(String subjectId, PredictRequest body) {
        return web.post().uri(uri -> uri.path("/predict/intent-ner").queryParam("subjectId", subjectId).build())
                .bodyValue(body).retrieve().bodyToMono(IntentNerResponse.class).block();
    }

    public PreviewResponse previewIntent(PreviewRequest body) {
        log.info("Preview intent: " + body);
        return web.post().uri("/preview/intent").bodyValue(body)
                .retrieve().bodyToMono(PreviewResponse.class).block();
    }
}

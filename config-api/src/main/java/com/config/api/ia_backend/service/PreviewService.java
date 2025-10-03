package com.config.api.ia_backend.service;

import com.config.api.ia_backend.client.PredictApiClient;
import com.config.api.ia_backend.dto.PreviewRequest;
import com.config.api.ia_backend.dto.PreviewResponse;
import org.springframework.stereotype.Service;

@Service
public class PreviewService {
    private final PredictApiClient client;
    public PreviewService(PredictApiClient client){ this.client = client; }
    public PreviewResponse preview(PreviewRequest req){ return client.previewIntent(req); }
}
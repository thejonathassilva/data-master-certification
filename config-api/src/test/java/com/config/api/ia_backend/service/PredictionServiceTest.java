package com.config.api.ia_backend.service;

import com.config.api.ia_backend.client.PredictApiClient;
import com.config.api.ia_backend.dto.IntentNerResponse;
import com.config.api.ia_backend.dto.PredictRequest;
import com.config.api.ia_backend.dto.SubjectClassifyResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

public class PredictionServiceTest {
    @Test
    void predict_ok(){
        var client = mock(PredictApiClient.class);
        var thresholds = mock(ThresholdService.class);
        var dialog = mock(DialogNodeService.class);
        var mapper = mock(ObjectMapper.class);

        var svc = new PredictionService(client, thresholds, dialog, mapper);
        var req = new PredictRequest("texto de teste");

        when(client.predictSubject("PF", req)).thenReturn(new SubjectClassifyResponse("subj1", java.util.Map.of("subj1",0.9)));
        var intent = new IntentNerResponse("INT_A", 0.85, List.of());
        when(client.predictIntentNer("subj1", req)).thenReturn(intent);
        when(thresholds.apply("subj1", intent)).thenReturn(intent);
        when(dialog.resolve("subj1", "INT_A", 0.85)).thenReturn(null);

        var resp = svc.predict("PF", req);
        assertEquals("subj1", resp.subjectId());
        assertEquals("INT_A", resp.intentId());
        assertEquals(0.85, resp.confidence(), 1e-6);
    }
}

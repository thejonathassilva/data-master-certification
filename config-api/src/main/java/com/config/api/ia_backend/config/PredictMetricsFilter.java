package com.facilita.configapi.audit;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@Component
public class PredictMetricsFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger("predict_audit");
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final int MAX_CHARS = 2048; // limita para não explodir log

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        // só filtra o /api/predict
        return !request.getRequestURI().equals("/api/predict");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        long start = System.nanoTime();

        // wrappers p/ ler corpo da request e response
        ContentCachingRequestWrapper reqWrapper = new ContentCachingRequestWrapper(request);
        ContentCachingResponseWrapper respWrapper = new ContentCachingResponseWrapper(response);

        try {
            filterChain.doFilter(reqWrapper, respWrapper);
        } finally {
            long durationMs = (System.nanoTime() - start) / 1_000_000;

            String channel = reqWrapper.getParameter("channel");
            int status = respWrapper.getStatus();

            String reqBody = truncate(new String(reqWrapper.getContentAsByteArray(), StandardCharsets.UTF_8));
            String respBody = truncate(new String(respWrapper.getContentAsByteArray(), StandardCharsets.UTF_8));

            Map<String, Object> event = new HashMap<>();
            event.put("ts", Instant.now().toString());
            event.put("path", reqWrapper.getRequestURI());
            event.put("method", reqWrapper.getMethod());
            event.put("channel", channel);
            event.put("status", status);
            event.put("duration_ms", durationMs);
            event.put("request_text", reqBody);
            event.put("response_text", respBody);

            try {
                log.info(MAPPER.writeValueAsString(event));
            } catch (Exception e) {
                log.warn("Erro ao gerar log JSON", e);
            }

            // copiar o body da response de volta pro output real
            respWrapper.copyBodyToResponse();
        }
    }

    private String truncate(String s) {
        if (s == null) return null;
        return s.length() > MAX_CHARS ? s.substring(0, MAX_CHARS) + "...(truncated)" : s;
    }
}

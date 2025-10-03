package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.dialogNodes.DialogNodeCreateRequest;
import com.config.api.ia_backend.dto.dialogNodes.DialogNodeResponse;
import com.config.api.ia_backend.dto.dialogNodes.DialogNodeUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.DialogNode;
import com.config.api.ia_backend.model.IntentDef;
import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.DialogNodeRepository;
import com.config.api.ia_backend.repository.IntentRepository;
import com.config.api.ia_backend.repository.SubjectRepository;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.common.protocol.types.Field;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@AllArgsConstructor
@Slf4j
public class DialogNodeService {
    private final DialogNodeRepository dialogNodeRepository;
    private final IntentRepository intentRepository;
    private final SubjectRepository subjectRepository;

    public DialogNodeResponse create(DialogNodeCreateRequest request){
        subjectRepository.findById(request.subjectId()).orElseThrow(() -> new BadRequestException("subjectId inválido"));
        DialogNode dialogNode = dialogNodeRepository.save(DialogNode.builder()
                .subjectId(request.subjectId())
                .name(request.name())
                .condition(new DialogNode.Condition(request.conditionType(), request.conditionValue()))
                .response(new DialogNode.Response(request.responseText(), request.responseActions()))
                .children(request.children())
                .build());
        return map(dialogNode);
    }

    public DialogNodeResponse get(String id){
        return map(dialogNodeRepository.findById(id).orElseThrow(() -> new NotFoundException("Dialog node not found")));
    }

    public List<DialogNodeResponse> list(String subjectId){
        var list = (subjectId==null) ? dialogNodeRepository.findAll() : dialogNodeRepository.findBySubjectId(subjectId);
        return list.stream().map(this::map).toList();
    }

    public DialogNodeResponse update(String id, DialogNodeUpdateRequest request){
        DialogNode dialogNode = dialogNodeRepository.findById(id).orElseThrow(() -> new NotFoundException("Dialog node not found"));
        if (request.name() != null) dialogNode.setName(request.name());
        if (request.conditionType() != null || request.conditionValue()!=null){
            var condition = dialogNode.getCondition()==null ? new DialogNode.Condition(null,null) : dialogNode.getCondition();
            if (request.conditionType() != null) condition.setType(request.conditionType());
            if (request.conditionValue() != null) condition.setValue(request.conditionValue());
            dialogNode.setCondition(condition);
        }
        if (request.responseText()!=null || request.responseActions()!=null){
            var response = dialogNode.getResponse() == null ? new DialogNode.Response(null, null) : dialogNode.getResponse();
            if (request.responseText() != null) response.setText(request.responseText());
            if (request.responseActions() != null) response.setActions(request.responseActions());
            dialogNode.setResponse(response);
        }
        if (request.children() != null) dialogNode.setChildren(request.children());
        return map(dialogNodeRepository.save(dialogNode));
    }

    public void delete(String id){
        if (!dialogNodeRepository.existsById(id)) throw new NotFoundException("Dialog node not found");
        dialogNodeRepository.deleteById(id);
    }

    private DialogNodeResponse map(DialogNode dialogNode){
        var cond = dialogNode.getCondition();
        var response = dialogNode.getResponse();
        return new DialogNodeResponse(
                dialogNode.getId(), dialogNode.getSubjectId(), dialogNode.getName(),
                cond != null ? cond.getType() : null, cond != null ? cond.getValue() : null,
                response != null ? response.getText() : null, response!=null? response.getActions() : null,
                dialogNode.getChildren()
        );
    }

    public Object resolve(String subjectName, String intentName, double confidence) {
        Subject subject = subjectRepository.findByName(subjectName);
        if (subject == null) {
            log.warn("[dialog.resolve] subject not found by name={}", subjectName);
            return null;
        }

        List<DialogNode> nodes = dialogNodeRepository.findBySubjectId(subject.getId());
        if (nodes == null || nodes.isEmpty()) {
            log.warn("[dialog.resolve] no nodes for subjectId={}", subject.getId());
            return null;
        }

        IntentDef intent = intentRepository.findFirstByName(intentName);
        if (intent == null) {
            log.warn("[dialog.resolve] intent not found by name={} (subjectId={})", intentName, subject.getId());
        }

        final String intentIdStr  = intent != null && intent.getId() != null ? intent.getId().toString() : null;
        final String intentNameLc = intentName != null ? intentName.trim().toLowerCase() : null;

        Optional<DialogNode> byIntent = nodes.stream()
                .filter(n -> n.getCondition() != null && "intent".equalsIgnoreCase(n.getCondition().getType()))
                .filter(n -> {
                    String raw = n.getCondition().getValue();
                    if (raw == null) return false;

                    if ("*".equals(raw.trim())) return true;

                    // divide por "|", normaliza e remove vazios
                    String[] parts = raw.split("\\|");
                    for (String p : parts) {
                        String token = p == null ? "" : p.trim();
                        if (token.isEmpty()) continue;

                        if (intentNameLc != null && token.equalsIgnoreCase(intentNameLc)) {
                            return true;
                        }
                        if (intentIdStr != null && token.equals(intentIdStr)) {
                            return true;
                        }
                    }
                    return false;
                })
                .findFirst();

        if (log.isDebugEnabled()) {
            log.warn("[dialog.resolve] try by-intent: intentId={} intentName={} matchedNodeId={}",
                    intentIdStr, intentName, byIntent.map(DialogNode::getId).orElse(null));
        }

        DialogNode node = byIntent.orElseGet(() ->
                nodes.stream()
                        .filter(n -> n.getCondition() != null && "true".equalsIgnoreCase(n.getCondition().getType()))
                        .findFirst()
                        .orElse(null)
        );

        if (node == null) {
            log.warn("[dialog.resolve] no matching node (subjectId={}, intentName={})", subject.getId(), intentName);
            return null;
        }

        return java.util.Map.of(
                "id", node.getId(),
                "name", node.getName(),
                "text", node.getResponse() != null ? node.getResponse().getText() : null,
                "actions", node.getResponse() != null ? node.getResponse().getActions() : java.util.List.of(),
                "children", node.getChildren() != null ? node.getChildren() : java.util.List.of()
        );
    }

    public Object resolveJAssistant(String subjectId, String intentName, double confidence) {
        Subject subject = subjectRepository.findById(subjectId).orElse(null);
        if (subject == null) {
            log.warn("[dialog.resolve] subject not found by name={}", subjectId);
            return null;
        }

        List<DialogNode> nodes = dialogNodeRepository.findBySubjectId(subject.getId());
        if (nodes == null || nodes.isEmpty()) {
            log.warn("[dialog.resolve] no nodes for subjectId={}", subject.getId());
            return null;
        }

        IntentDef intent = intentRepository.findFirstByName(intentName);
        if (intent == null) {
            log.warn("[dialog.resolve] intent not found by name={} (subjectId={})", intentName, subject.getId());
        }

        final String intentIdStr  = intent != null && intent.getId() != null ? intent.getId().toString() : null;
        final String intentNameLc = intentName != null ? intentName.trim().toLowerCase() : null;

        Optional<DialogNode> byIntent = nodes.stream()
                .filter(n -> n.getCondition() != null && "intent".equalsIgnoreCase(n.getCondition().getType()))
                .filter(n -> {
                    String raw = n.getCondition().getValue();
                    if (raw == null) return false;

                    if ("*".equals(raw.trim())) return true;

                    // divide por "|", normaliza e remove vazios
                    String[] parts = raw.split("\\|");
                    for (String p : parts) {
                        String token = p == null ? "" : p.trim();
                        if (token.isEmpty()) continue;

                        if (intentNameLc != null && token.equalsIgnoreCase(intentNameLc)) {
                            return true;
                        }
                        if (intentIdStr != null && token.equals(intentIdStr)) {
                            return true;
                        }
                    }
                    return false;
                })
                .findFirst();

        if (log.isDebugEnabled()) {
            log.warn("[dialog.resolve] try by-intent: intentId={} intentName={} matchedNodeId={}",
                    intentIdStr, intentName, byIntent.map(DialogNode::getId).orElse(null));
        }

        DialogNode node = byIntent.orElseGet(() ->
                nodes.stream()
                        .filter(n -> n.getCondition() != null && "true".equalsIgnoreCase(n.getCondition().getType()))
                        .findFirst()
                        .orElse(null)
        );

        if (node == null) {
            log.warn("[dialog.resolve] no matching node (subjectId={}, intentName={})", subject.getId(), intentName);
            return null;
        }

        return java.util.Map.of(
                "id", node.getId(),
                "name", node.getName(),
                "text", node.getResponse() != null ? node.getResponse().getText() : null,
                "actions", node.getResponse() != null ? node.getResponse().getActions() : java.util.List.of(),
                "children", node.getChildren() != null ? node.getChildren() : java.util.List.of()
        );
    }
}


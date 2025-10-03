package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.dialogNodes.DialogNodeCreateRequest;
import com.config.api.ia_backend.dto.dialogNodes.DialogNodeResponse;
import com.config.api.ia_backend.dto.dialogNodes.DialogNodeUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.DialogNode;
import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.DialogNodeRepository;
import com.config.api.ia_backend.repository.SubjectRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DialogNodeServiceTest {

    @Mock
    DialogNodeRepository repo;
    @Mock
    SubjectRepository subjects;
    @InjectMocks DialogNodeService service;

    @Test
    void create_ok() {
        when(subjects.findById("sub1")).thenReturn(Optional.of(new Subject()));
        when(repo.save(any(DialogNode.class))).thenAnswer(inv -> {
            DialogNode n = inv.getArgument(0);
            n.setId("node1");
            return n;
        });

        var req = new DialogNodeCreateRequest(
                "sub1","no-assistencia","intent","INT_ASSISTENCIA",
                "Você deseja acionar assistência 24h?", List.of("LOG"),
                List.of()
        );
        DialogNodeResponse out = service.create(req);

        assertEquals("node1", out.id());
        assertEquals("intent", out.conditionType());
        assertEquals("INT_ASSISTENCIA", out.conditionValue());
        assertEquals("Você deseja acionar assistência 24h?", out.responseText());
    }

    @Test
    void create_invalidSubject() {
        when(subjects.findById("x")).thenReturn(Optional.empty());
        var req = new DialogNodeCreateRequest("x","n","intent","Y","txt", List.of(), List.of());
        assertThrows(BadRequestException.class, () -> service.create(req));
    }

    @Test
    void update_ok() {
        DialogNode persisted = DialogNode.builder()
                .id("n1").subjectId("sub1").name("old")
                .condition(new DialogNode.Condition("intent","INT_X"))
                .response(new DialogNode.Response("txt", List.of()))
                .children(List.of())
                .build();
        when(repo.findById("n1")).thenReturn(Optional.of(persisted));
        when(repo.save(any(DialogNode.class))).thenAnswer(inv -> inv.getArgument(0));

        var out = service.update("n1", new DialogNodeUpdateRequest(
                "novo","expr","len(text)>5","novo texto", List.of("AUDIT"), List.of("child1")
        ));
        assertEquals("novo", out.name());
        assertEquals("expr", out.conditionType());
        assertEquals("len(text)>5", out.conditionValue());
        assertEquals("novo texto", out.responseText());
        assertEquals(1, out.responseActions().size());
        assertEquals(1, out.children().size());
    }

    @Test
    void get_notFound() {
        when(repo.findById("x")).thenReturn(Optional.empty());
        assertThrows(NotFoundException.class, () -> service.get("x"));
    }

    @Test
    void list_bySubject_ok() {
        when(repo.findBySubjectId("sub1")).thenReturn(List.of(
                DialogNode.builder().id("n1").subjectId("sub1").name("A").build()
        ));
        var list = service.list("sub1");
        assertEquals(1, list.size());
        assertEquals("A", list.get(0).name());
    }
}


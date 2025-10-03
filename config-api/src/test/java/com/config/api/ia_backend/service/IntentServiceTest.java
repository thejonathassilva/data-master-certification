package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.intent.IntentCreateRequest;
import com.config.api.ia_backend.dto.intent.IntentResponse;
import com.config.api.ia_backend.dto.intent.IntentUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.IntentDef;
import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.IntentRepository;
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
class IntentServiceTest {

    @Mock
    IntentRepository repo;
    @Mock
    SubjectRepository subjects;
    @InjectMocks IntentService service;

    @Test
    void create_ok() {
        when(subjects.findById("sub1")).thenReturn(Optional.of(new Subject()));
        when(repo.save(any(IntentDef.class))).thenAnswer(inv -> {
            IntentDef i = inv.getArgument(0);
            i.setId("int1");
            return i;
        });

        var req = new IntentCreateRequest("sub1", "ABRIR_SINISTRO", List.of("abrir sinistro", "abrir assistência"), true);
        IntentResponse out = service.create(req);

        assertEquals("int1", out.id());
        assertEquals("ABRIR_SINISTRO", out.name());
        assertTrue(out.active());
        assertEquals(2, out.examples().size());
    }

    @Test
    void create_invalidSubject() {
        when(subjects.findById("x")).thenReturn(Optional.empty());
        var req = new IntentCreateRequest("x", "NOME", List.of("a"), true);
        assertThrows(BadRequestException.class, () -> service.create(req));
    }

    @Test
    void update_ok() {
        IntentDef persisted = IntentDef.builder().id("int1").subjectId("sub1").name("OLD").examples(List.of("a")).active(true).build();
        when(repo.findById("int1")).thenReturn(Optional.of(persisted));
        when(repo.save(any(IntentDef.class))).thenAnswer(inv -> inv.getArgument(0));

        var out = service.update("int1", new IntentUpdateRequest("NEW", List.of("b","c"), false));
        assertEquals("NEW", out.name());
        assertEquals(2, out.examples().size());
        assertFalse(out.active());
    }

    @Test
    void get_notFound() {
        when(repo.findById("x")).thenReturn(Optional.empty());
        assertThrows(NotFoundException.class, () -> service.get("x"));
    }

    @Test
    void list_bySubject_ok() {
        when(repo.findBySubjectId("sub1")).thenReturn(List.of(
                IntentDef.builder().id("i1").subjectId("sub1").name("A").build()
        ));
        var list = service.list("sub1");
        assertEquals(1, list.size());
        assertEquals("A", list.get(0).name());
    }
}


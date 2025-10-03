package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.entities.EntityCreateRequest;
import com.config.api.ia_backend.dto.entities.EntityResponse;
import com.config.api.ia_backend.dto.entities.EntityUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.EntityDef;
import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.EntityRepository;
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
class EntityServiceTest {

    @Mock
    EntityRepository repo;
    @Mock
    SubjectRepository subjects;
    @InjectMocks EntityService service;

    @Test
    void create_ok() {
        when(subjects.findById("sub1")).thenReturn(Optional.of(new Subject()));
        when(repo.save(any(EntityDef.class))).thenAnswer(inv -> {
            EntityDef e = inv.getArgument(0);
            e.setId("ent1");
            return e;
        });

        var req = new EntityCreateRequest("sub1", "PLACA_VEICULO", List.of("[A-Z]{3}\\d{4}"), List.of());
        EntityResponse out = service.create(req);

        assertEquals("ent1", out.id());
        assertEquals("PLACA_VEICULO", out.name());
        assertEquals(1, out.patterns().size());
    }

    @Test
    void create_invalidSubject() {
        when(subjects.findById("x")).thenReturn(Optional.empty());
        var req = new EntityCreateRequest("x", "ANY", List.of(), List.of());
        assertThrows(BadRequestException.class, () -> service.create(req));
    }

    @Test
    void update_ok() {
        EntityDef persisted = EntityDef.builder().id("ent1").subjectId("sub1").name("OLD").patterns(List.of("p1")).gazetteer(List.of()).build();
        when(repo.findById("ent1")).thenReturn(Optional.of(persisted));
        when(repo.save(any(EntityDef.class))).thenAnswer(inv -> inv.getArgument(0));

        var out = service.update("ent1", new EntityUpdateRequest("NEW", List.of("p2","p3"), List.of("g1")));
        assertEquals("NEW", out.name());
        assertEquals(2, out.patterns().size());
        assertEquals(1, out.gazetteer().size());
    }

    @Test
    void get_notFound() {
        when(repo.findById("x")).thenReturn(Optional.empty());
        assertThrows(NotFoundException.class, () -> service.get("x"));
    }
}


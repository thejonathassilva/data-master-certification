package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.subject.SubjectCreateRequest;
import com.config.api.ia_backend.dto.subject.SubjectResponse;
import com.config.api.ia_backend.dto.subject.SubjectUpdateRequest;
import com.config.api.ia_backend.exception.BadRequestException;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.Channel;
import com.config.api.ia_backend.model.Subject;
import com.config.api.ia_backend.repository.ChannelRepository;
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
class SubjectServiceTest {

    @Mock
    SubjectRepository repo;
    @Mock
    ChannelRepository channels;
    @InjectMocks SubjectService service;

    @Test
    void create_ok() {
        when(channels.findById("ch1")).thenReturn(Optional.of(new Channel()));
        when(repo.save(any(Subject.class))).thenAnswer(inv -> {
            Subject s = inv.getArgument(0);
            s.setId("sub1");
            return s;
        });
        var req = new SubjectCreateRequest("ch1", "Seguro Assistência PF", 0.6, 0.5);
        SubjectResponse out = service.create(req);

        assertEquals("sub1", out.id());
        assertEquals("ch1", out.channelId());
        assertEquals(0.6, out.intentMinConf());
        assertEquals(0.5, out.entityMinConf());
    }

    @Test
    void create_invalidChannel() {
        when(channels.findById("chX")).thenReturn(Optional.empty());
        var req = new SubjectCreateRequest("chX", "Name", 0.5, 0.4);
        assertThrows(BadRequestException.class, () -> service.create(req));
    }

    @Test
    void get_notFound() {
        when(repo.findById("no")).thenReturn(Optional.empty());
        assertThrows(NotFoundException.class, () -> service.get("no"));
    }

    @Test
    void list_byChannel_ok() {
        when(repo.findByChannelId("ch1")).thenReturn(List.of(
                Subject.builder().id("s1").channelId("ch1").name("A").build()
        ));
        var list = service.list("ch1");
        assertEquals(1, list.size());
        assertEquals("A", list.get(0).name());
    }

    @Test
    void update_thresholds_and_version_ok() {
        Subject s = Subject.builder()
                .id("s1").channelId("ch1").name("A")
                .thresholds(new Subject.Thresholds(0.5, 0.4))
                .activeModelVersion("v1").build();

        when(repo.findById("s1")).thenReturn(Optional.of(s));
        when(repo.save(any(Subject.class))).thenAnswer(inv -> inv.getArgument(0));

        var req = new SubjectUpdateRequest("A2", 0.7, 0.6, "v2");
        var out = service.update("s1", req);

        assertEquals("A2", out.name());
        assertEquals("v2", out.activeModelVersion());
        assertEquals(0.7, out.intentMinConf());
        assertEquals(0.6, out.entityMinConf());
    }
}


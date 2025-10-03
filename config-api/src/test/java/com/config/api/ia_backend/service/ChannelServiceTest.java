package com.config.api.ia_backend.service;

import com.config.api.ia_backend.dto.channel.ChannelCreateRequest;
import com.config.api.ia_backend.dto.channel.ChannelResponse;
import com.config.api.ia_backend.dto.channel.ChannelUpdateRequest;
import com.config.api.ia_backend.exception.NotFoundException;
import com.config.api.ia_backend.model.Channel;
import com.config.api.ia_backend.repository.ChannelRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ChannelServiceTest {

    @Mock
    ChannelRepository repo;
    @InjectMocks ChannelService service;

    @Test
    void create_ok() {
        var req = new ChannelCreateRequest("PF", 0.6);
        ArgumentCaptor<Channel> capt = ArgumentCaptor.forClass(Channel.class);
        when(repo.save(any(Channel.class))).thenAnswer(inv -> {
            Channel c = inv.getArgument(0);
            c.setId("ch1");
            return c;
        });

        ChannelResponse out = service.create(req);

        verify(repo).save(capt.capture());
        assertEquals("PF", capt.getValue().getName());
        assertEquals(0.6, capt.getValue().getMinConfSubject());

        assertEquals("ch1", out.id());
        assertEquals("PF", out.name());
        assertEquals(0.6, out.minConfSubject());
    }

    @Test
    void get_notFound() {
        when(repo.findById("x")).thenReturn(Optional.empty());
        assertThrows(NotFoundException.class, () -> service.get("x"));
    }

    @Test
    void list_ok() {
        when(repo.findAll()).thenReturn(List.of(
                Channel.builder().id("ch1").name("PF").minConfSubject(0.5).build(),
                Channel.builder().id("ch2").name("PJ").minConfSubject(0.7).build()
        ));
        var list = service.list();
        assertEquals(2, list.size());
        assertEquals("PF", list.get(0).name());
    }

    @Test
    void update_ok() {
        Channel persisted = Channel.builder().id("ch1").name("PF").minConfSubject(0.5).build();
        when(repo.findById("ch1")).thenReturn(Optional.of(persisted));
        when(repo.save(any(Channel.class))).thenAnswer(inv -> inv.getArgument(0));

        var out = service.update("ch1", new ChannelUpdateRequest("PF-NEW", 0.9));

        assertEquals("PF-NEW", out.name());
        assertEquals(0.9, out.minConfSubject());
    }

    @Test
    void delete_notFound() {
        when(repo.existsById("x")).thenReturn(false);
        assertThrows(NotFoundException.class, () -> service.delete("x"));
    }

    @Test
    void delete_ok() {
        when(repo.existsById("ch1")).thenReturn(true);
        service.delete("ch1");
        verify(repo).deleteById("ch1");
    }
}


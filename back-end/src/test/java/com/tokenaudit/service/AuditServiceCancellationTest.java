package com.tokenaudit.service;

import com.tokenaudit.config.AppProperties;
import com.tokenaudit.entity.AuditRecord;
import com.tokenaudit.mapper.AuditEventMapper;
import com.tokenaudit.mapper.AuditRecordMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.core.env.Environment;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.*;

class AuditServiceCancellationTest {
    private AuditRecordMapper recordMapper;
    private AuditEventMapper eventMapper;
    private AuditService service;

    @BeforeEach
    void setUp() {
        recordMapper = mock(AuditRecordMapper.class);
        eventMapper = mock(AuditEventMapper.class);
        AppProperties properties = new AppProperties();
        properties.setAuditMaxConcurrency(2);
        properties.setAuditQueueCapacity(8);
        properties.setAuditProcessTimeoutSeconds(30);
        service = new AuditService(
                mock(TokenService.class),
                recordMapper,
                eventMapper,
                mock(AuditAiConfigService.class),
                properties,
                mock(Environment.class)
        );
    }

    @AfterEach
    void tearDown() {
        service.shutdown();
    }

    @Test
    void cancelsADetachedRunningAuditIdempotently() {
        AuditRecord running = record(17L, "running", "{}");
        AuditRecord cancelled = record(17L, "cancelled", "{\"cancelled\":true}");
        when(recordMapper.findById(17L)).thenReturn(running, cancelled);
        when(recordMapper.updateResultIfRunning(any(AuditRecord.class))).thenReturn(1);

        Map<String, Object> result = service.cancelAudit(17L);

        assertEquals("cancelled", result.get("status"));
        assertEquals(100, result.get("progress"));
        verify(recordMapper).updateResultIfRunning(argThat(record -> "cancelled".equals(record.getStatus())));
        verify(eventMapper).insert(argThat(event -> "audit_cancelled".equals(event.getEvent())));
    }

    @Test
    void leavesACompletedAuditUntouched() {
        AuditRecord completed = record(18L, "completed", "{}");
        when(recordMapper.findById(18L)).thenReturn(completed);

        Map<String, Object> result = service.cancelAudit(18L);

        assertEquals("completed", result.get("status"));
        verify(recordMapper, never()).updateResultIfRunning(any());
    }

    private AuditRecord record(Long id, String status, String reportJson) {
        AuditRecord record = new AuditRecord();
        record.setId(id);
        record.setTokenId(7L);
        record.setAuditTime("2026-08-22 19:00:00");
        record.setStatus(status);
        record.setReportJson(reportJson);
        return record;
    }
}

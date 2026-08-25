package com.tokenaudit.controller;

import com.tokenaudit.dto.AuditResponse;
import com.tokenaudit.dto.AuditStartRequest;
import com.tokenaudit.service.AuditService;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class AuditControllerTest {
    @Test
    void deepEndpointUsesTheStableDeepServiceBoundary() {
        AuditService service = mock(AuditService.class);
        AuditController controller = new AuditController(service);
        AuditStartRequest request = new AuditStartRequest();
        request.setTokenId(7L);
        request.setExportFormats(List.of("json", "md"));
        request.setAuditDimensions(List.of("validity", "security"));
        request.setAuditRounds(3);
        request.setAdaptiveEarlyStop(true);

        AuditResponse expected = new AuditResponse();
        expected.setAuditId(88L);
        expected.setAuditMode("deep");
        when(service.startDeepAudit(7L, request.getExportFormats(), request.getAuditDimensions(), 3, true)).thenReturn(expected);

        AuditResponse response = controller.startDeep(request);

        assertEquals(88L, response.getAuditId());
        assertEquals("deep", response.getAuditMode());
        verify(service).startDeepAudit(7L, request.getExportFormats(), request.getAuditDimensions(), 3, true);
    }

    @Test
    void deleteEndpointDelegatesToTheAuditService() {
        AuditService service = mock(AuditService.class);
        AuditController controller = new AuditController(service);

        controller.delete(52L);

        verify(service).deleteAudit(52L);
    }
}

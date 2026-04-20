package com.tokenaudit.controller;

import com.tokenaudit.dto.AuditResponse;
import com.tokenaudit.dto.AuditStartRequest;
import com.tokenaudit.service.AuditService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/audits")
public class AuditController {
    private final AuditService auditService;

    public AuditController(AuditService auditService) {
        this.auditService = auditService;
    }

    @PostMapping
    public AuditResponse start(@Valid @RequestBody AuditStartRequest req) {
        return auditService.startAudit(req.getTokenId(), req.getExportFormats());
    }

    @GetMapping("/{id}")
    public Map<String, Object> get(@PathVariable("id") Long id) {
        return auditService.getAudit(id);
    }

    @GetMapping
    public List<Map<String, Object>> list(@RequestParam(value = "tokenId", required = false) Long tokenId) {
        return auditService.listAudits(tokenId);
    }

    @GetMapping("/{id}/events")
    public List<Map<String, Object>> events(@PathVariable("id") Long id) {
        return auditService.listEvents(id);
    }
}

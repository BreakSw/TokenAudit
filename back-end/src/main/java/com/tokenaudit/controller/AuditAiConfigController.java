package com.tokenaudit.controller;

import com.tokenaudit.dto.AuditAiConfigRequest;
import com.tokenaudit.dto.AuditAiConfigResponse;
import com.tokenaudit.service.AuditAiConfigService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/settings/audit-ai")
public class AuditAiConfigController {
    private final AuditAiConfigService service;

    public AuditAiConfigController(AuditAiConfigService service) {
        this.service = service;
    }

    @GetMapping
    public AuditAiConfigResponse get() { return service.getConfig(); }

    @PutMapping
    public AuditAiConfigResponse save(@Valid @RequestBody AuditAiConfigRequest request) {
        return service.save(request);
    }

    @DeleteMapping
    public void delete() { service.delete(); }
}

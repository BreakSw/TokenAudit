package com.tokenaudit.dto;

import jakarta.validation.constraints.NotNull;

import java.util.List;

public class AuditStartRequest {
    @NotNull
    private Long tokenId;
    private List<String> exportFormats;
    private List<String> auditDimensions;

    public Long getTokenId() {
        return tokenId;
    }

    public void setTokenId(Long tokenId) {
        this.tokenId = tokenId;
    }

    public List<String> getExportFormats() {
        return exportFormats;
    }

    public void setExportFormats(List<String> exportFormats) {
        this.exportFormats = exportFormats;
    }

    public List<String> getAuditDimensions() {
        return auditDimensions;
    }

    public void setAuditDimensions(List<String> auditDimensions) {
        this.auditDimensions = auditDimensions;
    }
}

package com.tokenaudit.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

import java.util.List;

public class AuditStartRequest {
    @NotNull
    private Long tokenId;
    private List<String> exportFormats;
    private List<String> auditDimensions;
    @Min(1)
    @Max(5)
    private Integer auditRounds = 2;
    private Boolean adaptiveEarlyStop = false;

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

    public Integer getAuditRounds() {
        return auditRounds;
    }

    public void setAuditRounds(Integer auditRounds) {
        this.auditRounds = auditRounds;
    }

    public Boolean getAdaptiveEarlyStop() {
        return adaptiveEarlyStop;
    }

    public void setAdaptiveEarlyStop(Boolean adaptiveEarlyStop) {
        this.adaptiveEarlyStop = adaptiveEarlyStop;
    }
}

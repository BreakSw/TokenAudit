package com.tokenaudit.dto;

import java.util.Map;

public class AuditResponse {
    private Long auditId;
    private String auditMode;
    private Map<String, Object> report;

    public Long getAuditId() {
        return auditId;
    }

    public void setAuditId(Long auditId) {
        this.auditId = auditId;
    }

    public String getAuditMode() {
        return auditMode;
    }

    public void setAuditMode(String auditMode) {
        this.auditMode = auditMode;
    }

    public Map<String, Object> getReport() {
        return report;
    }

    public void setReport(Map<String, Object> report) {
        this.report = report;
    }
}

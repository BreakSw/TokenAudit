package com.tokenaudit.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String apiKey;
    private String pythonExecutable;
    private String auditCoreWorkingDir;
    private String auditExportFormats;

    public String getApiKey() {
        return apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    public String getPythonExecutable() {
        return pythonExecutable;
    }

    public void setPythonExecutable(String pythonExecutable) {
        this.pythonExecutable = pythonExecutable;
    }

    public String getAuditCoreWorkingDir() {
        return auditCoreWorkingDir;
    }

    public void setAuditCoreWorkingDir(String auditCoreWorkingDir) {
        this.auditCoreWorkingDir = auditCoreWorkingDir;
    }

    public String getAuditExportFormats() {
        return auditExportFormats;
    }

    public void setAuditExportFormats(String auditExportFormats) {
        this.auditExportFormats = auditExportFormats;
    }
}

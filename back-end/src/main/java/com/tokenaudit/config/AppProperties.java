package com.tokenaudit.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String apiKey;
    private String pythonExecutable;
    private String auditCoreWorkingDir;
    private String auditExportFormats;
    private String environment;
    private String allowedOrigins;
    private boolean allowPrivateAuditTargets;
    private String tokenEncryptionKey;
    private String tokenEncryptionKeyFile;
    private int auditMaxConcurrency;
    private int auditQueueCapacity;
    private long auditProcessTimeoutSeconds;

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

    public String getEnvironment() { return environment; }
    public void setEnvironment(String environment) { this.environment = environment; }
    public String getAllowedOrigins() { return allowedOrigins; }
    public void setAllowedOrigins(String allowedOrigins) { this.allowedOrigins = allowedOrigins; }
    public boolean isAllowPrivateAuditTargets() { return allowPrivateAuditTargets; }
    public void setAllowPrivateAuditTargets(boolean allowPrivateAuditTargets) { this.allowPrivateAuditTargets = allowPrivateAuditTargets; }
    public String getTokenEncryptionKey() { return tokenEncryptionKey; }
    public void setTokenEncryptionKey(String tokenEncryptionKey) { this.tokenEncryptionKey = tokenEncryptionKey; }
    public String getTokenEncryptionKeyFile() { return tokenEncryptionKeyFile; }
    public void setTokenEncryptionKeyFile(String tokenEncryptionKeyFile) { this.tokenEncryptionKeyFile = tokenEncryptionKeyFile; }
    public int getAuditMaxConcurrency() { return auditMaxConcurrency; }
    public void setAuditMaxConcurrency(int auditMaxConcurrency) { this.auditMaxConcurrency = auditMaxConcurrency; }
    public int getAuditQueueCapacity() { return auditQueueCapacity; }
    public void setAuditQueueCapacity(int auditQueueCapacity) { this.auditQueueCapacity = auditQueueCapacity; }
    public long getAuditProcessTimeoutSeconds() { return auditProcessTimeoutSeconds; }
    public void setAuditProcessTimeoutSeconds(long auditProcessTimeoutSeconds) { this.auditProcessTimeoutSeconds = auditProcessTimeoutSeconds; }
}

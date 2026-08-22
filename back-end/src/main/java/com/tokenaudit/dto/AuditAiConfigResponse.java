package com.tokenaudit.dto;

public class AuditAiConfigResponse {
    private boolean configured;
    private String provider;
    private String apiUrl;
    private String model;
    private String apiKeyMasked;
    private Long expiresInSeconds;
    private Long ttlMinutes;

    public boolean isConfigured() { return configured; }
    public void setConfigured(boolean configured) { this.configured = configured; }
    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    public String getApiUrl() { return apiUrl; }
    public void setApiUrl(String apiUrl) { this.apiUrl = apiUrl; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getApiKeyMasked() { return apiKeyMasked; }
    public void setApiKeyMasked(String apiKeyMasked) { this.apiKeyMasked = apiKeyMasked; }
    public Long getExpiresInSeconds() { return expiresInSeconds; }
    public void setExpiresInSeconds(Long expiresInSeconds) { this.expiresInSeconds = expiresInSeconds; }
    public Long getTtlMinutes() { return ttlMinutes; }
    public void setTtlMinutes(Long ttlMinutes) { this.ttlMinutes = ttlMinutes; }
}

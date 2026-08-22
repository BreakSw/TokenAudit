package com.tokenaudit.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public class AuditAiConfigRequest {
    @NotBlank
    private String provider;
    @NotBlank
    private String apiUrl;
    @NotBlank
    private String model;
    private String apiKey;
    @Min(1)
    @Max(43200)
    private long ttlMinutes;

    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    public String getApiUrl() { return apiUrl; }
    public void setApiUrl(String apiUrl) { this.apiUrl = apiUrl; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }
    public long getTtlMinutes() { return ttlMinutes; }
    public void setTtlMinutes(long ttlMinutes) { this.ttlMinutes = ttlMinutes; }
}

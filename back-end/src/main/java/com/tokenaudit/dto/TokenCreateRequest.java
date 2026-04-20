package com.tokenaudit.dto;

import jakarta.validation.constraints.NotBlank;

public class TokenCreateRequest {
    @NotBlank
    private String name;
    @NotBlank
    private String token;
    @NotBlank
    private String platform;
    @NotBlank
    private String tokenBaseUrl;
    @NotBlank
    private String claimedModel;
    @NotBlank
    private String nonClaimedModel;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getPlatform() {
        return platform;
    }

    public void setPlatform(String platform) {
        this.platform = platform;
    }

    public String getTokenBaseUrl() {
        return tokenBaseUrl;
    }

    public void setTokenBaseUrl(String tokenBaseUrl) {
        this.tokenBaseUrl = tokenBaseUrl;
    }

    public String getClaimedModel() {
        return claimedModel;
    }

    public void setClaimedModel(String claimedModel) {
        this.claimedModel = claimedModel;
    }

    public String getNonClaimedModel() {
        return nonClaimedModel;
    }

    public void setNonClaimedModel(String nonClaimedModel) {
        this.nonClaimedModel = nonClaimedModel;
    }
}

package com.tokenaudit.dto;

public class TokenResponse {
    private Long id;
    private String name;
    private String tokenMasked;
    private String platform;
    private String tokenBaseUrl;
    private String claimedModel;
    private String nonClaimedModel;
    private String createdAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getTokenMasked() {
        return tokenMasked;
    }

    public void setTokenMasked(String tokenMasked) {
        this.tokenMasked = tokenMasked;
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

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }
}

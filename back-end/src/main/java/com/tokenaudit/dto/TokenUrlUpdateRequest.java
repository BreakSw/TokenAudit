package com.tokenaudit.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class TokenUrlUpdateRequest {
    @NotBlank
    @Size(max = 2048)
    private String tokenBaseUrl;

    public String getTokenBaseUrl() {
        return tokenBaseUrl;
    }

    public void setTokenBaseUrl(String tokenBaseUrl) {
        this.tokenBaseUrl = tokenBaseUrl;
    }
}

package com.tokenaudit.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class TokenModelUpdateRequest {
    @NotBlank
    @Size(max = 255)
    private String claimedModel;

    public String getClaimedModel() {
        return claimedModel;
    }

    public void setClaimedModel(String claimedModel) {
        this.claimedModel = claimedModel;
    }
}

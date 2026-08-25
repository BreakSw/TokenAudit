package com.tokenaudit.controller;

import com.tokenaudit.dto.TokenCreateRequest;
import com.tokenaudit.dto.TokenModelUpdateRequest;
import com.tokenaudit.dto.TokenResponse;
import com.tokenaudit.dto.TokenUrlUpdateRequest;
import com.tokenaudit.service.TokenService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tokens")
public class TokenController {
    private final TokenService tokenService;

    public TokenController(TokenService tokenService) {
        this.tokenService = tokenService;
    }

    @PostMapping
    public TokenResponse create(@Valid @RequestBody TokenCreateRequest req) {
        return tokenService.create(req);
    }

    @GetMapping
    public List<TokenResponse> list() {
        return tokenService.list();
    }

    @PutMapping("/{id}/model")
    public TokenResponse updateClaimedModel(
            @PathVariable("id") Long id,
            @Valid @RequestBody TokenModelUpdateRequest req
    ) {
        return tokenService.updateClaimedModel(id, req.getClaimedModel());
    }

    @PutMapping("/{id}/url")
    public TokenResponse updateTokenBaseUrl(
            @PathVariable("id") Long id,
            @Valid @RequestBody TokenUrlUpdateRequest req
    ) {
        return tokenService.updateTokenBaseUrl(id, req.getTokenBaseUrl());
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable("id") Long id) {
        tokenService.delete(id);
    }
}


package com.tokenaudit.service;

import com.tokenaudit.dto.TokenResponse;
import com.tokenaudit.entity.TokenInfo;
import com.tokenaudit.exception.ApiException;
import com.tokenaudit.mapper.TokenInfoMapper;
import com.tokenaudit.security.OutboundUrlValidator;
import com.tokenaudit.security.TokenCipher;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

class TokenServiceTest {
    private TokenInfoMapper mapper;
    private TokenCipher cipher;
    private OutboundUrlValidator validator;
    private TokenService service;

    @BeforeEach
    void setUp() {
        mapper = mock(TokenInfoMapper.class);
        cipher = mock(TokenCipher.class);
        validator = mock(OutboundUrlValidator.class);
        service = new TokenService(mapper, cipher, validator);
    }

    @Test
    void updatesOnlyTheClaimedModelAndReturnsAMaskedToken() {
        TokenInfo stored = new TokenInfo();
        stored.setId(4L);
        stored.setName("Relay");
        stored.setToken("encrypted-token");
        stored.setPlatform("Any relay");
        stored.setTokenBaseUrl("https://relay.example/v1");
        stored.setClaimedModel("vendor/new-model");
        stored.setNonClaimedModel("");
        stored.setCreatedAt("2026-08-22 14:00:00");

        when(mapper.updateClaimedModel(4L, "vendor/new-model")).thenReturn(1);
        when(mapper.findById(4L)).thenReturn(stored);
        when(cipher.isEncrypted("encrypted-token")).thenReturn(true);
        when(cipher.decrypt("encrypted-token")).thenReturn("secret-token-value");

        TokenResponse response = service.updateClaimedModel(4L, "  vendor/new-model  ");

        assertEquals("vendor/new-model", response.getClaimedModel());
        assertEquals("secr***alue", response.getTokenMasked());
        verify(mapper).updateClaimedModel(4L, "vendor/new-model");
        verify(mapper, never()).updateToken(eq(4L), anyString());
    }

    @Test
    void reportsAMissingTokenInsteadOfCreatingOne() {
        when(mapper.updateClaimedModel(404L, "model")).thenReturn(0);

        ApiException error = assertThrows(
                ApiException.class,
                () -> service.updateClaimedModel(404L, "model")
        );

        assertEquals("token_not_found", error.getMessage());
        verify(mapper, never()).findById(anyLong());
    }

    @Test
    void validatesAndUpdatesOnlyTheTokenBaseUrl() {
        TokenInfo stored = new TokenInfo();
        stored.setId(4L);
        stored.setName("Relay");
        stored.setToken("encrypted-token");
        stored.setPlatform("Any relay");
        stored.setTokenBaseUrl("https://new-relay.example/v1");
        stored.setClaimedModel("vendor/model");
        stored.setNonClaimedModel("");
        stored.setCreatedAt("2026-08-22 14:00:00");

        when(validator.validate("  https://new-relay.example/v1/  ")).thenReturn("https://new-relay.example/v1");
        when(mapper.updateTokenBaseUrl(4L, "https://new-relay.example/v1")).thenReturn(1);
        when(mapper.findById(4L)).thenReturn(stored);
        when(cipher.isEncrypted("encrypted-token")).thenReturn(true);
        when(cipher.decrypt("encrypted-token")).thenReturn("secret-token-value");

        TokenResponse response = service.updateTokenBaseUrl(4L, "  https://new-relay.example/v1/  ");

        assertEquals("https://new-relay.example/v1", response.getTokenBaseUrl());
        assertEquals("secr***alue", response.getTokenMasked());
        verify(mapper).updateTokenBaseUrl(4L, "https://new-relay.example/v1");
        verify(mapper, never()).updateClaimedModel(anyLong(), anyString());
    }
}

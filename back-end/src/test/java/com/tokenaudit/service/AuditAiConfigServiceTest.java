package com.tokenaudit.service;

import com.tokenaudit.dto.AuditAiConfigRequest;
import com.tokenaudit.dto.AuditAiConfigResponse;
import com.tokenaudit.exception.ApiException;
import com.tokenaudit.security.OutboundUrlValidator;
import com.tokenaudit.security.TokenCipher;
import com.tokenaudit.util.JsonUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.time.Duration;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class AuditAiConfigServiceTest {
    private StringRedisTemplate redis;
    private ValueOperations<String, String> values;
    private AuditAiConfigService service;

    @BeforeEach
    @SuppressWarnings("unchecked")
    void setUp() {
        redis = mock(StringRedisTemplate.class);
        values = mock(ValueOperations.class);
        when(redis.opsForValue()).thenReturn(values);
        TokenCipher cipher = TokenCipher.fromBase64Key("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=");
        service = new AuditAiConfigService(redis, cipher, new OutboundUrlValidator(true));
    }

    @Test
    void encryptsTheKeyAndSetsTheRequestedTtlOnEverySave() {
        AuditAiConfigRequest request = request("secret-api-key", 180);

        AuditAiConfigResponse response = service.save(request);

        ArgumentCaptor<String> json = ArgumentCaptor.forClass(String.class);
        verify(values).set(eq(AuditAiConfigService.REDIS_KEY), json.capture(), eq(Duration.ofMinutes(180)));
        Map<String, Object> stored = JsonUtil.toMap(json.getValue());
        assertNotEquals("secret-api-key", stored.get("encryptedApiKey"));
        assertTrue(String.valueOf(stored.get("encryptedApiKey")).startsWith("enc:v1:"));
        assertEquals("secr***-key", response.getApiKeyMasked());
        assertEquals(10800L, response.getExpiresInSeconds());
    }

    @Test
    void blankKeyRetainsTheEncryptedKeyAndResetsTtl() {
        service.save(request("secret-api-key", 60));
        ArgumentCaptor<String> firstJson = ArgumentCaptor.forClass(String.class);
        verify(values).set(eq(AuditAiConfigService.REDIS_KEY), firstJson.capture(), eq(Duration.ofMinutes(60)));
        when(values.get(AuditAiConfigService.REDIS_KEY)).thenReturn(firstJson.getValue());

        service.save(request("", 240));

        ArgumentCaptor<String> allJson = ArgumentCaptor.forClass(String.class);
        verify(values, times(2)).set(eq(AuditAiConfigService.REDIS_KEY), allJson.capture(), any(Duration.class));
        Map<String, Object> first = JsonUtil.toMap(allJson.getAllValues().get(0));
        Map<String, Object> second = JsonUtil.toMap(allJson.getAllValues().get(1));
        assertEquals(first.get("encryptedApiKey"), second.get("encryptedApiKey"));
        verify(values).set(eq(AuditAiConfigService.REDIS_KEY), anyString(), eq(Duration.ofMinutes(240)));
    }

    @Test
    void getNeverReturnsThePlaintextKey() {
        service.save(request("secret-api-key", 60));
        ArgumentCaptor<String> json = ArgumentCaptor.forClass(String.class);
        verify(values).set(eq(AuditAiConfigService.REDIS_KEY), json.capture(), any(Duration.class));
        when(values.get(AuditAiConfigService.REDIS_KEY)).thenReturn(json.getValue());
        when(redis.getExpire(AuditAiConfigService.REDIS_KEY, TimeUnit.SECONDS)).thenReturn(3000L);

        AuditAiConfigResponse response = service.getConfig();

        assertTrue(response.isConfigured());
        assertEquals("secr***-key", response.getApiKeyMasked());
        assertEquals(3000L, response.getExpiresInSeconds());
    }

    @Test
    void missingOrExpiredConfigurationBlocksAuditStart() {
        when(values.get(AuditAiConfigService.REDIS_KEY)).thenReturn(null);

        ApiException error = assertThrows(ApiException.class, service::requireActiveConfig);

        assertEquals("audit_ai_not_configured", error.getMessage());
    }

    private AuditAiConfigRequest request(String apiKey, long ttlMinutes) {
        AuditAiConfigRequest request = new AuditAiConfigRequest();
        request.setProvider("OpenRouter");
        request.setApiUrl("https://openrouter.ai/api/v1/chat/completions");
        request.setModel("openai/gpt-4o-mini");
        request.setApiKey(apiKey);
        request.setTtlMinutes(ttlMinutes);
        return request;
    }
}

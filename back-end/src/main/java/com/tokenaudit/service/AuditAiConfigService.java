package com.tokenaudit.service;

import com.tokenaudit.dto.AuditAiConfigRequest;
import com.tokenaudit.dto.AuditAiConfigResponse;
import com.tokenaudit.exception.ApiException;
import com.tokenaudit.security.OutboundUrlValidator;
import com.tokenaudit.security.TokenCipher;
import com.tokenaudit.util.JsonUtil;
import org.springframework.dao.DataAccessException;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
public class AuditAiConfigService {
    static final String REDIS_KEY = "tokenaudit:settings:audit-ai";
    private final StringRedisTemplate redis;
    private final TokenCipher tokenCipher;
    private final OutboundUrlValidator urlValidator;

    public AuditAiConfigService(StringRedisTemplate redis, TokenCipher tokenCipher, OutboundUrlValidator urlValidator) {
        this.redis = redis;
        this.tokenCipher = tokenCipher;
        this.urlValidator = urlValidator;
    }

    public AuditAiConfigResponse getConfig() {
        try {
            String raw = redis.opsForValue().get(REDIS_KEY);
            if (raw == null || raw.isBlank()) return emptyResponse();
            Map<String, Object> stored = JsonUtil.toMap(raw);
            long expires = redis.getExpire(REDIS_KEY, TimeUnit.SECONDS);
            if (expires <= 0) return emptyResponse();
            return toResponse(stored, expires);
        } catch (DataAccessException error) {
            throw new ApiException("redis_unavailable");
        } catch (ApiException error) {
            throw error;
        } catch (Exception error) {
            throw new ApiException("audit_ai_config_invalid");
        }
    }

    public AuditAiConfigResponse save(AuditAiConfigRequest request) {
        try {
            String provider = trim(request.getProvider());
            String apiUrl = urlValidator.validateAuditAiEndpoint(request.getApiUrl());
            String model = trim(request.getModel());
            long ttlMinutes = request.getTtlMinutes();
            String apiKey = trim(request.getApiKey());

            if (provider.isEmpty() || model.isEmpty() || ttlMinutes < 1 || ttlMinutes > 43200) {
                throw new ApiException("invalid_audit_ai_config");
            }

            String encryptedApiKey;
            if (!apiKey.isEmpty()) {
                encryptedApiKey = tokenCipher.encrypt(apiKey);
            } else {
                String existingRaw = redis.opsForValue().get(REDIS_KEY);
                if (existingRaw == null || existingRaw.isBlank()) {
                    throw new ApiException("audit_ai_api_key_required");
                }
                encryptedApiKey = stringValue(JsonUtil.toMap(existingRaw).get("encryptedApiKey"));
                if (encryptedApiKey.isBlank()) throw new ApiException("audit_ai_api_key_required");
            }

            Map<String, Object> stored = new LinkedHashMap<>();
            stored.put("provider", provider);
            stored.put("apiUrl", apiUrl);
            stored.put("model", model);
            stored.put("encryptedApiKey", encryptedApiKey);
            stored.put("ttlMinutes", ttlMinutes);
            stored.put("updatedAt", Instant.now().toString());
            redis.opsForValue().set(REDIS_KEY, JsonUtil.toJson(stored), Duration.ofMinutes(ttlMinutes));
            return toResponse(stored, TimeUnit.MINUTES.toSeconds(ttlMinutes));
        } catch (DataAccessException error) {
            throw new ApiException("redis_unavailable");
        }
    }

    public void delete() {
        try {
            redis.delete(REDIS_KEY);
        } catch (DataAccessException error) {
            throw new ApiException("redis_unavailable");
        }
    }

    public RuntimeConfig requireActiveConfig() {
        try {
            String raw = redis.opsForValue().get(REDIS_KEY);
            if (raw == null || raw.isBlank()) throw new ApiException("audit_ai_not_configured");
            Map<String, Object> stored = JsonUtil.toMap(raw);
            String encryptedApiKey = stringValue(stored.get("encryptedApiKey"));
            String apiUrl = stringValue(stored.get("apiUrl"));
            String model = stringValue(stored.get("model"));
            if (encryptedApiKey.isBlank() || apiUrl.isBlank() || model.isBlank()) {
                throw new ApiException("audit_ai_not_configured");
            }
            return new RuntimeConfig(
                    stringValue(stored.get("provider")),
                    urlValidator.validateAuditAiEndpoint(apiUrl),
                    model,
                    tokenCipher.decrypt(encryptedApiKey)
            );
        } catch (DataAccessException error) {
            throw new ApiException("redis_unavailable");
        } catch (ApiException error) {
            throw error;
        } catch (Exception error) {
            throw new ApiException("audit_ai_config_invalid");
        }
    }

    private AuditAiConfigResponse toResponse(Map<String, Object> stored, long expires) {
        AuditAiConfigResponse response = new AuditAiConfigResponse();
        response.setConfigured(true);
        response.setProvider(stringValue(stored.get("provider")));
        response.setApiUrl(stringValue(stored.get("apiUrl")));
        response.setModel(stringValue(stored.get("model")));
        response.setApiKeyMasked(mask(tokenCipher.decrypt(stringValue(stored.get("encryptedApiKey")))));
        response.setExpiresInSeconds(expires);
        response.setTtlMinutes(longValue(stored.get("ttlMinutes")));
        return response;
    }

    private AuditAiConfigResponse emptyResponse() {
        AuditAiConfigResponse response = new AuditAiConfigResponse();
        response.setConfigured(false);
        response.setExpiresInSeconds(0L);
        return response;
    }

    private String mask(String value) {
        if (value == null || value.isEmpty()) return "";
        if (value.length() <= 8) return "****";
        return value.substring(0, Math.min(4, value.length())) + "***" + value.substring(value.length() - 4);
    }

    private String trim(String value) { return value == null ? "" : value.trim(); }
    private String stringValue(Object value) { return value == null ? "" : String.valueOf(value); }
    private Long longValue(Object value) {
        if (value instanceof Number number) return number.longValue();
        try { return Long.parseLong(stringValue(value)); } catch (Exception ignored) { return null; }
    }

    public record RuntimeConfig(String provider, String apiUrl, String model, String apiKey) {}
}

package com.tokenaudit.security;

import com.tokenaudit.exception.ApiException;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class OutboundUrlValidatorTest {
    private final OutboundUrlValidator validator = new OutboundUrlValidator(false);

    @Test
    void acceptsPublicHttpServiceRootAndApiBasePath() {
        assertDoesNotThrow(() -> validator.validate("https://example.com"));
        assertEquals("https://openrouter.ai/api/v1", validator.validate("https://openrouter.ai/api/v1/"));
        assertEquals("https://example.com/compatible-mode/v1", validator.validate("https://example.com/compatible-mode/v1"));
        assertEquals("https://example.com/v1/chat/completions", validator.validate("https://example.com/v1/chat/completions"));
        assertEquals("https://example.com/v1/responses", validator.validate("https://example.com/v1/responses"));
    }

    @Test
    void rejectsLocalPrivateAndMetadataTargets() {
        assertInvalid("http://127.0.0.1:8080");
        assertInvalid("http://localhost:8080");
        assertInvalid("http://10.0.0.8");
        assertInvalid("http://169.254.169.254");
        assertInvalid("http://[::1]");
    }

    @Test
    void rejectsCredentialsQueriesFragmentsAndNonInferenceEndpointPaths() {
        assertInvalid("https://user:pass@example.com");
        assertInvalid("https://example.com?tenant=1");
        assertInvalid("https://example.com/#fragment");
        assertInvalid("https://example.com/v1/models");
        assertInvalid("ftp://example.com");
    }

    @Test
    void acceptsPublicAuditAiEndpointPathsButKeepsOtherUrlGuards() {
        assertEquals(
                "https://example.com/v1/chat/completions",
                validator.validateAuditAiEndpoint("https://example.com/v1/chat/completions")
        );
        ApiException error = assertThrows(ApiException.class,
                () -> validator.validateAuditAiEndpoint("https://example.com/v1/chat/completions?tenant=1"));
        assertEquals("invalid_audit_ai_url", error.getMessage());
    }

    private void assertInvalid(String value) {
        ApiException error = assertThrows(ApiException.class, () -> validator.validate(value));
        assertEquals("invalid_token_base_url", error.getMessage());
    }
}

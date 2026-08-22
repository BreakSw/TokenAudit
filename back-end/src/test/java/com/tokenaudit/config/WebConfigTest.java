package com.tokenaudit.config;

import org.junit.jupiter.api.Test;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class WebConfigTest {
    @Test
    void allowsAuditAiConfigurationPutRequestsFromTheFrontend() {
        AppProperties properties = new AppProperties();
        properties.setAllowedOrigins("http://localhost:5173");
        ExposedCorsRegistry registry = new ExposedCorsRegistry();

        new WebConfig(properties).addCorsMappings(registry);

        CorsConfiguration configuration = registry.configurations().get("/**");
        assertNotNull(configuration);
        assertTrue(configuration.getAllowedMethods().contains("PUT"));
        assertEquals("http://localhost:5173", configuration.getAllowedOrigins().get(0));
    }

    private static class ExposedCorsRegistry extends CorsRegistry {
        Map<String, CorsConfiguration> configurations() {
            return getCorsConfigurations();
        }
    }
}

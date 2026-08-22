package com.tokenaudit.config;

import com.tokenaudit.security.OutboundUrlValidator;
import com.tokenaudit.security.TokenCipher;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.util.Base64;

@Configuration
public class SecurityBeansConfig {
    @Bean
    TokenCipher tokenCipher(AppProperties props) {
        String configured = trim(props.getTokenEncryptionKey());
        if (!configured.isEmpty()) {
            return TokenCipher.fromBase64Key(configured);
        }
        if ("production".equalsIgnoreCase(trim(props.getEnvironment()))) {
            throw new IllegalStateException("TOKEN_ENCRYPTION_KEY is required in production");
        }

        try {
            Path path = Path.of(trim(props.getTokenEncryptionKeyFile()).isEmpty()
                    ? "../data/token-encryption.key"
                    : props.getTokenEncryptionKeyFile()).toAbsolutePath().normalize();
            if (Files.exists(path)) {
                return TokenCipher.fromBase64Key(Files.readString(path, StandardCharsets.UTF_8).trim());
            }
            Files.createDirectories(path.getParent());
            byte[] key = new byte[32];
            new SecureRandom().nextBytes(key);
            String encoded = Base64.getEncoder().encodeToString(key);
            Files.writeString(path, encoded, StandardCharsets.UTF_8);
            return TokenCipher.fromBase64Key(encoded);
        } catch (Exception error) {
            throw new IllegalStateException("Unable to load or create token encryption key", error);
        }
    }

    @Bean
    OutboundUrlValidator outboundUrlValidator(AppProperties props) {
        return new OutboundUrlValidator(props.isAllowPrivateAuditTargets());
    }

    private String trim(String value) {
        return value == null ? "" : value.trim();
    }
}

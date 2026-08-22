package com.tokenaudit.security;

import org.junit.jupiter.api.Test;

import java.util.Base64;

import static org.junit.jupiter.api.Assertions.*;

class TokenCipherTest {
    @Test
    void encryptsWithRandomNonceAndDecryptsBothCiphertexts() {
        String key = Base64.getEncoder().encodeToString(new byte[32]);
        TokenCipher cipher = TokenCipher.fromBase64Key(key);

        String first = cipher.encrypt("sk-sensitive-token");
        String second = cipher.encrypt("sk-sensitive-token");

        assertTrue(cipher.isEncrypted(first));
        assertNotEquals(first, second);
        assertFalse(first.contains("sk-sensitive-token"));
        assertEquals("sk-sensitive-token", cipher.decrypt(first));
        assertEquals("sk-sensitive-token", cipher.decrypt(second));
    }

    @Test
    void rejectsMalformedKey() {
        assertThrows(IllegalArgumentException.class, () -> TokenCipher.fromBase64Key("not-a-key"));
    }
}

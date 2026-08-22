package com.tokenaudit.security;

import com.tokenaudit.exception.ApiException;

import java.net.InetAddress;
import java.net.URI;
import java.util.Locale;

public final class OutboundUrlValidator {
    private final boolean allowPrivateTargets;

    public OutboundUrlValidator(boolean allowPrivateTargets) {
        this.allowPrivateTargets = allowPrivateTargets;
    }

    public String validate(String rawUrl) {
        return validate(rawUrl, "invalid_token_base_url");
    }

    public String validateAuditAiEndpoint(String rawUrl) {
        return validate(rawUrl, "invalid_audit_ai_url");
    }

    private String validate(String rawUrl, String errorCode) {
        try {
            URI uri = URI.create(rawUrl == null ? "" : rawUrl.trim());
            String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(Locale.ROOT);
            if (!(scheme.equals("http") || scheme.equals("https")) || uri.getHost() == null) {
                throw invalid(errorCode);
            }
            if (uri.getUserInfo() != null || uri.getQuery() != null || uri.getFragment() != null) {
                throw invalid(errorCode);
            }
            String path = uri.getPath();
            if (hasUnsafePath(uri, path) || isModelsEndpoint(path)) {
                throw invalid(errorCode);
            }
            if (!allowPrivateTargets) {
                String host = uri.getHost();
                if (host.equalsIgnoreCase("localhost") || host.endsWith(".localhost")) {
                    throw invalid(errorCode);
                }
                for (InetAddress address : InetAddress.getAllByName(host)) {
                    if (isUnsafe(address)) {
                        throw invalid(errorCode);
                    }
                }
            }
            String authority = uri.getPort() < 0 ? uri.getHost() : uri.getHost() + ":" + uri.getPort();
            if (uri.getHost().contains(":")) {
                authority = "[" + uri.getHost() + "]" + (uri.getPort() < 0 ? "" : ":" + uri.getPort());
            }
            String normalizedPath = normalizePath(path);
            return scheme + "://" + authority + normalizedPath;
        } catch (ApiException error) {
            throw error;
        } catch (Exception error) {
            throw invalid(errorCode);
        }
    }

    private boolean hasUnsafePath(URI uri, String path) {
        String rawPath = uri.getRawPath();
        if (rawPath != null && rawPath.contains("\\")) return true;
        if (path == null || path.isBlank()) return false;
        for (String segment : path.split("/")) {
            if (segment.equals(".") || segment.equals("..")) return true;
        }
        return false;
    }

    private boolean isModelsEndpoint(String path) {
        String normalized = normalizePath(path).toLowerCase(Locale.ROOT);
        return normalized.endsWith("/models");
    }

    private String normalizePath(String path) {
        if (path == null || path.isBlank() || path.equals("/")) return "";
        String normalized = path;
        while (normalized.endsWith("/") && normalized.length() > 1) {
            normalized = normalized.substring(0, normalized.length() - 1);
        }
        return normalized;
    }

    private boolean isUnsafe(InetAddress address) {
        return address.isAnyLocalAddress()
                || address.isLoopbackAddress()
                || address.isLinkLocalAddress()
                || address.isSiteLocalAddress()
                || address.isMulticastAddress();
    }

    private ApiException invalid(String errorCode) {
        return new ApiException(errorCode);
    }
}

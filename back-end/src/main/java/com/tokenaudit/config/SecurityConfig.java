package com.tokenaudit.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Configuration
public class SecurityConfig {

    @Bean
    public OncePerRequestFilter apiKeyFilter(AppProperties props) {
        return new OncePerRequestFilter() {
            @Override
            protected boolean shouldNotFilter(HttpServletRequest request) {
                String path = request.getRequestURI();
                return !path.startsWith("/api/");
            }

            @Override
            protected void doFilterInternal(
                    HttpServletRequest request,
                    HttpServletResponse response,
                    FilterChain filterChain
            ) throws ServletException, IOException {
                String configured = props.getApiKey();
                if (configured == null || configured.isBlank()) {
                    filterChain.doFilter(request, response);
                    return;
                }

                String key = request.getHeader("X-API-KEY");
                if (key != null && key.equals(configured)) {
                    filterChain.doFilter(request, response);
                    return;
                }

                if (HttpMethod.OPTIONS.matches(request.getMethod())) {
                    filterChain.doFilter(request, response);
                    return;
                }

                response.setStatus(401);
                response.setContentType("application/json;charset=UTF-8");
                response.getWriter().write("{\"error\":\"unauthorized\"}");
            }
        };
    }
}


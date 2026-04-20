package com.tokenaudit.service;

import com.tokenaudit.dto.TokenCreateRequest;
import com.tokenaudit.dto.TokenResponse;
import com.tokenaudit.entity.TokenInfo;
import com.tokenaudit.exception.ApiException;
import com.tokenaudit.mapper.TokenInfoMapper;
import com.tokenaudit.util.DateUtil;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class TokenService {
    private final TokenInfoMapper tokenInfoMapper;

    public TokenService(TokenInfoMapper tokenInfoMapper) {
        this.tokenInfoMapper = tokenInfoMapper;
    }

    public TokenResponse create(TokenCreateRequest req) {
        TokenInfo entity = new TokenInfo();
        entity.setName(req.getName());
        entity.setToken(req.getToken());
        entity.setPlatform(req.getPlatform());
        entity.setTokenBaseUrl(req.getTokenBaseUrl());
        entity.setClaimedModel(req.getClaimedModel());
        entity.setNonClaimedModel(req.getNonClaimedModel());
        entity.setCreatedAt(DateUtil.now());
        tokenInfoMapper.insert(entity);
        return toResponse(entity);
    }

    public List<TokenResponse> list() {
        List<TokenInfo> all = tokenInfoMapper.findAll();
        List<TokenResponse> res = new ArrayList<>();
        for (TokenInfo t : all) {
            res.add(toResponse(t));
        }
        return res;
    }

    public TokenInfo getEntity(Long id) {
        TokenInfo t = tokenInfoMapper.findById(id);
        if (t == null) {
            throw new ApiException("token_not_found");
        }
        return t;
    }

    public void delete(Long id) {
        int n = tokenInfoMapper.deleteById(id);
        if (n <= 0) {
            throw new ApiException("token_not_found");
        }
    }

    private TokenResponse toResponse(TokenInfo t) {
        TokenResponse r = new TokenResponse();
        r.setId(t.getId());
        r.setName(t.getName());
        r.setTokenMasked(mask(t.getToken()));
        r.setPlatform(t.getPlatform());
        r.setTokenBaseUrl(t.getTokenBaseUrl());
        r.setClaimedModel(t.getClaimedModel());
        r.setNonClaimedModel(t.getNonClaimedModel());
        r.setCreatedAt(t.getCreatedAt());
        return r;
    }

    private String mask(String token) {
        if (token == null || token.isBlank()) {
            return "";
        }
        int keepStart = Math.min(4, token.length());
        int keepEnd = Math.min(4, Math.max(0, token.length() - keepStart));
        if (token.length() <= keepStart + keepEnd + 3) {
            return token.substring(0, Math.min(2, token.length())) + "***";
        }
        return token.substring(0, keepStart) + "***" + token.substring(token.length() - keepEnd);
    }
}


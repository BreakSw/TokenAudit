package com.tokenaudit.mapper;

import com.tokenaudit.entity.TokenInfo;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface TokenInfoMapper {
    @Insert("INSERT INTO token_info(name, token, platform, token_base_url, claimed_model, non_claimed_model, created_at) " +
            "VALUES(#{name}, #{token}, #{platform}, #{tokenBaseUrl}, #{claimedModel}, #{nonClaimedModel}, #{createdAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(TokenInfo tokenInfo);

    @Select("SELECT * FROM token_info ORDER BY id DESC")
    List<TokenInfo> findAll();

    @Select("SELECT * FROM token_info WHERE id = #{id}")
    TokenInfo findById(@Param("id") Long id);

    @Delete("DELETE FROM token_info WHERE id = #{id}")
    int deleteById(@Param("id") Long id);
}


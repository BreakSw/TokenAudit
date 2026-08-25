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

    @Update("UPDATE token_info SET token = #{token} WHERE id = #{id}")
    int updateToken(@Param("id") Long id, @Param("token") String token);

    @Update("UPDATE token_info SET claimed_model = #{claimedModel} WHERE id = #{id}")
    int updateClaimedModel(@Param("id") Long id, @Param("claimedModel") String claimedModel);

    @Update("UPDATE token_info SET token_base_url = #{tokenBaseUrl} WHERE id = #{id}")
    int updateTokenBaseUrl(@Param("id") Long id, @Param("tokenBaseUrl") String tokenBaseUrl);
}


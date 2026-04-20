package com.tokenaudit.mapper;

import com.tokenaudit.entity.AuditRecord;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface AuditRecordMapper {
    @Insert("INSERT INTO audit_record(token_id, audit_time, status, overall_conclusion, report_json, created_at) " +
            "VALUES(#{tokenId}, #{auditTime}, #{status}, #{overallConclusion}, #{reportJson}, #{createdAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(AuditRecord record);

    @Select("SELECT * FROM audit_record WHERE id = #{id}")
    AuditRecord findById(@Param("id") Long id);

    @Select("SELECT * FROM audit_record WHERE token_id = #{tokenId} ORDER BY id DESC")
    List<AuditRecord> findByTokenId(@Param("tokenId") Long tokenId);

    @Select("SELECT * FROM audit_record ORDER BY id DESC")
    List<AuditRecord> findAll();

    @Update("UPDATE audit_record SET status=#{status}, overall_conclusion=#{overallConclusion}, report_json=#{reportJson} WHERE id=#{id}")
    int updateResult(AuditRecord record);
}

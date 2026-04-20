package com.tokenaudit.mapper;

import com.tokenaudit.entity.AuditEvent;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface AuditEventMapper {
    @Insert("INSERT INTO audit_event(audit_id, ts, event, payload_json) VALUES(#{auditId}, #{ts}, #{event}, #{payloadJson})")
    int insert(AuditEvent e);

    @Select("SELECT * FROM audit_event WHERE audit_id = #{auditId} ORDER BY id ASC")
    List<AuditEvent> listByAuditId(@Param("auditId") Long auditId);

    @Select("SELECT COUNT(*) FROM audit_event WHERE audit_id = #{auditId} AND event IN ('token_call_end','deepseek_call_end')")
    int countProgressOps(@Param("auditId") Long auditId);
}


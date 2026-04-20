package com.tokenaudit;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.mybatis.spring.annotation.MapperScan;

@SpringBootApplication
@MapperScan("com.tokenaudit.mapper")
public class TokenAuditApplication {
    public static void main(String[] args) {
        SpringApplication.run(TokenAuditApplication.class, args);
    }
}

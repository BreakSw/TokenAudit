package com.tokenaudit.config;

import org.springframework.beans.factory.InitializingBean;
import org.springframework.stereotype.Component;

import java.io.File;

@Component
public class DatabaseInit implements InitializingBean {
    @Override
    public void afterPropertiesSet() {
        File dir = new File("../data/database");
        dir.mkdirs();
    }
}


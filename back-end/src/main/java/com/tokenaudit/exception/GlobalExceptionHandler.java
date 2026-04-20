package com.tokenaudit.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ApiException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, Object> handleApi(ApiException ex) {
        Map<String, Object> m = new HashMap<>();
        m.put("error", ex.getMessage());
        return m;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, Object> handleValidation(MethodArgumentNotValidException ex) {
        Map<String, Object> m = new HashMap<>();
        m.put("error", "validation_error");
        m.put("detail", ex.getBindingResult().getAllErrors());
        return m;
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Map<String, Object> handle(Exception ex) {
        Map<String, Object> m = new HashMap<>();
        m.put("error", "internal_error");
        m.put("message", ex.getMessage());
        return m;
    }
}


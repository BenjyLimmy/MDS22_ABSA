package com.example.demo.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        // // Global configuration
        registry.addMapping("/**")
                .allowedOrigins("*")  // Consider restricting to specific domains in production
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(false)  // Set to true if you need cookies/auth
                .maxAge(3600);  // 1 hour cache for CORS preflight requests
    }
}

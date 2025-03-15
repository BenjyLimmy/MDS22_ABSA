package com.example.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.service.LaptopService;

import java.io.IOException;

@RestController
public class LaptopController {

    @Autowired
    private LaptopService laptopService;

    @GetMapping("/import")
    public ResponseEntity<String> importDataAll() {
        // import data from all files in sample_datasets
        try {
            laptopService.importDataFromDirectory("sample_datasets");
            return ResponseEntity.ok("Data imported successfully from all files in sample_datasets.");
        } catch (IOException e) {
            return ResponseEntity.badRequest().body("Error importing data: " + e.getMessage());
        }
    }
}
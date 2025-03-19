package com.example.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.model.Laptop;
import com.example.demo.service.LaptopService;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

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

    @GetMapping("/laptops")
    public ResponseEntity<List<Laptop>> getAllLaptops(@RequestParam(required = false) String aspects) {
        List<String> aspectList = aspects != null
                ? Arrays.asList(aspects.split(","))
                : Collections.emptyList();
                
        // For now, we're not using the aspects parameter
        List<Laptop> laptops = laptopService.getAllLaptops();
        return ResponseEntity.ok(laptops);
    }
}
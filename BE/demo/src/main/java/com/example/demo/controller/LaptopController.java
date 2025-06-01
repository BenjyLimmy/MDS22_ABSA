package com.example.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestMapping;
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
    public ResponseEntity<List<Laptop>> getLaptopsByAspects(@RequestParam(name = "aspects", required = false) String aspects) {
        List<String> aspectList = aspects != null  // Check if the 'aspects' parameter is provided
                ? Arrays.asList(aspects.split(","))  // Split the comma-separated aspects string into a list
                : Collections.emptyList();  // If 'aspects' is null, create an empty list

        List<Laptop> laptops = laptopService.getLaptopsByAspects(aspectList);
        return ResponseEntity.ok(laptops);
    }

    // Support both DELETE and GET for clearing data
    @RequestMapping(value = "/laptops/clear", method = {RequestMethod.DELETE, RequestMethod.GET})
    public ResponseEntity<String> clearAllData() {
        try {
            long deletedCount = laptopService.clearAllData();
            return ResponseEntity.ok("Successfully cleared " + deletedCount + " laptop records from the database.");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error clearing data: " + e.getMessage());
        }
    }

}
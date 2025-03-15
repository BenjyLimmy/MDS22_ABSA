package com.example.demo.service;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.core.io.Resource;
import org.springframework.core.io.support.ResourcePatternResolver;
import org.springframework.core.io.support.ResourcePatternUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demo.model.Laptop;
import com.example.demo.repository.LaptopRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class LaptopService {

    @Autowired
    private LaptopRepository laptopRepository;

    @Autowired
    private ResourcePatternResolver resourcePatternResolver;

    private static final Logger logger = LoggerFactory.getLogger(LaptopService.class);


    // import many files at once 
    public void importDataFromDirectory(String directoryPath) throws IOException {

        String locationPattern = "classpath:" + directoryPath + "/*.json";
        
        // Finds all files in the directory that match the pattern
        Resource[] resources = ResourcePatternUtils.getResourcePatternResolver(resourcePatternResolver).getResources(locationPattern);

        // Iterates through each file found in the directory
        for (Resource resource : resources) {
            // Checks if the file is readable before processing
            if (resource.isReadable()) {
                try (InputStream inputStream = resource.getInputStream()) {
                    // Creates an ObjectMapper to parse JSON
                    ObjectMapper objectMapper = new ObjectMapper();

                    // Reads the JSON file and converts it into a list of Laptop objects
                    List<Laptop> laptops = objectMapper.readValue(inputStream, new TypeReference<List<Laptop>>() {});

                    // Saves the list of Laptop objects to the MongoDB database
                    laptopRepository.saveAll(laptops);

                    logger.info("Successfully imported data from: {}", resource.getFilename());

                }catch (IOException e) {
                    logger.error("Failed to import data from: {}", resource.getFilename(), e);
                } catch (Exception e) {
                    logger.error("An unexpected error occurred while importing: {}", resource.getFilename(), e);
                }
            }
        }
    }
}

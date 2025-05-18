package com.example.demo.service;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.core.io.Resource;
import org.springframework.core.io.support.ResourcePatternResolver;
import org.springframework.core.io.support.ResourcePatternUtils;
import org.springframework.data.domain.PageRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;

import com.example.demo.model.Laptop;
import com.example.demo.model.ReviewSentiment;
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
    private static final String ASPECT_AUDIO = "AUDIO";
    private static final String ASPECT_BATTERY = "BATTERY";
    private static final String ASPECT_BUILD_QUALITY = "BUILD_QUALITY";
    private static final String ASPECT_DESIGN = "DESIGN";
    private static final String ASPECT_DISPLAY = "DISPLAY";
    private static final String ASPECT_PERFORMANCE = "PERFORMANCE";
    private static final String ASPECT_PORTABILITY = "PORTABILITY";
    private static final String ASPECT_PRICE = "PRICE";
    private static final int STAR_RATING_5 = 5;
    private static final int STAR_RATING_4 = 4;
    private static final int STAR_RATING_3 = 3;
    private static final int STAR_RATING_2 = 2;
    private static final int STAR_RATING_1 = 1;


    /**
     * Imports data from all JSON files in the specified directory.
     */
    public void importDataFromDirectory(String directoryPath) throws IOException {
        String locationPattern = "classpath:" + directoryPath + "/*.json";
        Resource[] resources = ResourcePatternUtils.getResourcePatternResolver(resourcePatternResolver).getResources(locationPattern);

        Stream.of(resources)
                .filter(Resource::isReadable)
                .forEach(this::processResource);
    }

    /**
     * Processes the JSON data and saving it to the database.
     */
    private void processResource(Resource resource) {
        try (InputStream inputStream = resource.getInputStream()) {
            List<Map<String, Object>> laptopMaps = new ObjectMapper()
                    .readValue(inputStream, new TypeReference<>() {});

            laptopMaps.forEach(laptopMap -> {
                Laptop laptop = calculateAspectScores(laptopMap);
                laptopRepository.save(laptop);
                
            });
            logger.info("Successfully imported data from: {}", resource.getFilename());
        } catch (IOException e) {
            logger.error("Failed to import data from: {}", resource.getFilename(), e);
        } catch (Exception e) {
            logger.error("An unexpected error occurred while importing: {}", resource.getFilename(), e);
        }
    }

    /**
     * Calculates and sets the aspect scores for a Laptop based on review sentiments.
     */
    public Laptop calculateAspectScores(Map<String, Object> productMap) {
        Laptop laptop = new ObjectMapper().convertValue(productMap, Laptop.class);
        ReviewSentiment sentiments = laptop.getReviewSentiments();

        if (sentiments == null) {
            // Set default values or return early
            laptop.setAudioScore(0);
            laptop.setBatteryScore(0);
            laptop.setBuildQualityScore(0);
            laptop.setDesignScore(0);
            laptop.setDisplayScore(0);
            laptop.setPerformanceScore(0);
            laptop.setPortabilityScore(0);
            laptop.setPriceScore(0);
            return laptop;
        }

        // Calculate and set scores for each aspect
        laptop.setAudioScore(calculateEachAspectScore(sentiments, ASPECT_AUDIO));
        laptop.setBatteryScore(calculateEachAspectScore(sentiments, ASPECT_BATTERY));
        laptop.setBuildQualityScore(calculateEachAspectScore(sentiments, ASPECT_BUILD_QUALITY));
        laptop.setDesignScore(calculateEachAspectScore(sentiments, ASPECT_DESIGN));
        laptop.setDisplayScore(calculateEachAspectScore(sentiments, ASPECT_DISPLAY));
        laptop.setPerformanceScore(calculateEachAspectScore(sentiments, ASPECT_PERFORMANCE));
        laptop.setPortabilityScore(calculateEachAspectScore(sentiments, ASPECT_PORTABILITY));
        laptop.setPriceScore(calculateEachAspectScore(sentiments, ASPECT_PRICE));

        return laptop;
    }
    
    /**
     * Calculates the score for a specific aspect based on review sentiments.
     */
    public int calculateEachAspectScore(ReviewSentiment sentiments, String aspect) {
        int score = 0;

        // Calculate score for each star rating and accumulate.
        score += calculateScoreForStar(sentiments.getPos5Aspects(), sentiments.getNeg5Aspects(), aspect, STAR_RATING_5);
        score += calculateScoreForStar(sentiments.getPos4Aspects(), sentiments.getNeg4Aspects(), aspect, STAR_RATING_4);
        score += calculateScoreForStar(sentiments.getPos3Aspects(), sentiments.getNeg3Aspects(), aspect, STAR_RATING_3);
        score += calculateScoreForStar(sentiments.getPos2Aspects(), sentiments.getNeg2Aspects(), aspect, STAR_RATING_2);
        score += calculateScoreForStar(sentiments.getPos1Aspects(), sentiments.getNeg1Aspects(), aspect, STAR_RATING_1);

        return score;
    }
    

    /**
     * Calculates the score for a specific aspect based on review sentiments for a specific star rating.
     */
    public int calculateScoreForStar(List<String> posAspects, List<String> negAspects, String aspect, int starRating) {
        int score = 0;

        if (posAspects != null) {
            int positiveCount = Collections.frequency(posAspects, aspect);
            score += positiveCount * starRating;
        }

        if (negAspects != null) {
            int negativeCount = Collections.frequency(negAspects, aspect);
            score -= negativeCount * (6 - starRating);
        }

        return score;
    }


    /**
     * Retrieves a list of 5 laptops based on specified aspects, sorted, or all if no aspects are provided. 
     */
    public List<Laptop> getLaptopsByAspects(List<String> aspects) {
        // Return all laptops if no aspects are specified
        if (aspects.isEmpty()) {
            return laptopRepository.findAll(Pageable.unpaged()).getContent();
        }

        // Create a Sort object based on the provided aspects
        Sort sort = createSortObject(aspects);
        // Limit to 5 laptops 
        Pageable pageable = PageRequest.of(0, 5, sort);

        // Retrieve the sorted laptops from the database
        return laptopRepository.findAll(pageable).getContent();
    }


    /**
     * Creates a Sort object based on a list of aspects, sorting in descending order for each
     */
    private Sort createSortObject(List<String> aspects) {
        Sort sort = Sort.unsorted();
        // sort by first aspect (descending), then by second aspect (descending) within the results of the first sort & so on 
        for (String aspect : aspects) {
            String fieldName = aspectNameToFieldName(aspect);
            if (fieldName != null) {
                sort = sort.and(Sort.by(fieldName).descending());
            }
        }
        return sort;
    }


    /**
     * Maps an aspect name to its corresponding field name in the Laptop entity
     */
    private String aspectNameToFieldName(String aspect) {
        return switch (aspect.toUpperCase()) {
            case "AUDIO" -> "audioScore";
            case "BATTERY" -> "batteryScore";
            case "BUILD_QUALITY" -> "buildQualityScore";
            case "DESIGN" -> "designScore";
            case "DISPLAY" -> "displayScore";
            case "PERFORMANCE" -> "performanceScore";
            case "PORTABILITY" -> "portabilityScore";
            case "PRICE" -> "priceScore";
            default -> null;
        };
    }
}

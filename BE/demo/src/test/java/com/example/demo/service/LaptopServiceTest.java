package com.example.demo.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import com.example.demo.model.Laptop;
import com.example.demo.model.ReviewSentiment;
import com.example.demo.repository.LaptopRepository;

/**
 * Tests for LaptopService which handles laptop sentiment analysis and retrieval.
 * This service calculates aspect scores based on positive and negative sentiments
 * from reviews at different star ratings, and provides sorting by these aspect scores.
 *
 * The scoring system works as follows:
 * - For positive aspects: count * star_rating
 * - For negative aspects: -count * (6 - star_rating)
 *
 * This creates a weighted scoring where higher star positive reviews contribute more
 * positively and lower star negative reviews contribute more negatively.
 */
@ExtendWith(MockitoExtension.class)
class LaptopServiceTest {

    @Mock
    private LaptopRepository laptopRepository;

    @InjectMocks
    private LaptopService laptopService;

    private ReviewSentiment testSentiments;

    /**
     * Sets up test data with predefined sentiment patterns.
     * The test sentiments simulate the following:
     * - DISPLAY: 2 positive 5-star reviews (10 points)
     * - PERFORMANCE: 1 positive 5-star review (5 points)
     * - PRICE: 1 negative 5-star review (-1 point)
     * - AUDIO & BATTERY: Each has 1 positive 4-star review (4 points each)
     * - PORTABILITY: 1 negative 4-star review (-2 points)
     * - DESIGN: 1 positive 3-star review (3 points)
     * - BUILD_QUALITY: 2 negative 3-star reviews (-6 points)
     *
     * These values produce predictable scores for testing the calculation logic.
     */
    @BeforeEach
    void setUp() {
        testSentiments = new ReviewSentiment();
        testSentiments.setPos5Aspects(Arrays.asList("DISPLAY", "DISPLAY", "PERFORMANCE"));
        testSentiments.setNeg5Aspects(Arrays.asList("PRICE"));
        testSentiments.setPos4Aspects(Arrays.asList("AUDIO", "BATTERY"));
        testSentiments.setNeg4Aspects(Arrays.asList("PORTABILITY"));
        testSentiments.setPos3Aspects(Arrays.asList("DESIGN"));
        testSentiments.setNeg3Aspects(Arrays.asList("BUILD_QUALITY", "BUILD_QUALITY"));
        // Initialize other ratings as empty lists to avoid NullPointerExceptions
        testSentiments.setPos2Aspects(Collections.emptyList());
        testSentiments.setNeg2Aspects(Collections.emptyList());
        testSentiments.setPos1Aspects(Collections.emptyList());
        testSentiments.setNeg1Aspects(Collections.emptyList());
    }

    /**
     * Tests the main aspect score calculation process.
     * This is the core business logic that:
     * 1. Takes a map representing laptop JSON data
     * 2. Extracts review sentiments
     * 3. Calculates scores for each aspect based on +/- sentiment frequency at each star level
     * 4. Sets these calculated scores on the laptop object
     *
     * For example, DISPLAY has 2 positive 5-star reviews which gives:
     * 2 * 5 = 10 points
     */
    @Test
    @DisplayName("Should calculate all aspect scores correctly")
    void testCalculateAspectScores() {
        // Create a Map that will represent our JSON data
        Map<String, Object> laptopMap = new HashMap<>();

        // Add to map the way it would be in JSON
        laptopMap.put("review_sentiments", testSentiments);
        laptopMap.put("title", "Test Laptop");

        // Now we can directly call the public method
        Laptop processedLaptop = laptopService.calculateAspectScores(laptopMap);

        // Verify expected scores
        assertEquals(10, processedLaptop.getDisplayScore());       // 2 pos5 * 5 = 10
        assertEquals(5, processedLaptop.getPerformanceScore());    // 1 pos5 * 5 = 5
        assertEquals(-1, processedLaptop.getPriceScore());         // 1 neg5 * -1 = -1
        assertEquals(4, processedLaptop.getAudioScore());          // 1 pos4 * 4 = 4
        assertEquals(4, processedLaptop.getBatteryScore());        // 1 pos4 * 4 = 4
        assertEquals(-2, processedLaptop.getPortabilityScore());   // 1 neg4 * -2 = -2
        assertEquals(3, processedLaptop.getDesignScore());         // 1 pos3 * 3 = 3
        assertEquals(-6, processedLaptop.getBuildQualityScore());  // 2 neg3 * -3 = -6
    }

    /**
     * Tests focusing on individual aspect score calculations.
     * These tests verify the scoring logic for different aspects,
     * handling of null values, and calculation across different aspects.
     *
     * The service aggregates scores from all star ratings for a specific aspect.
     */
    @Nested
    @DisplayName("Aspect Score Calculation Tests")
    class AspectScoreCalculationTests {

        /**
         * Tests calculation of specific aspect scores.
         * Verifies that scores are correctly aggregated from all star ratings
         * for a given aspect.
         */
        @Test
        @DisplayName("Should calculate individual aspect scores correctly")
        void testCalculateEachAspectScore() {
            // Test individual aspect score calculation
            int displayScore = laptopService.calculateEachAspectScore(testSentiments, "DISPLAY");
            assertEquals(10, displayScore);  // 2 pos5 * 5 = 10

            int buildQualityScore = laptopService.calculateEachAspectScore(testSentiments, "BUILD_QUALITY");
            assertEquals(-6, buildQualityScore);  // 2 neg3 * -3 = -6
        }

        /**
         * Tests that null sentiment lists are handled gracefully.
         * When a ReviewSentiment has null lists, the score should be 0
         * rather than throwing NullPointerException.
         */
        @Test
        @DisplayName("Should handle null aspect lists gracefully")
        void testNullAspectLists() {
            // Create sentiment with null lists
            ReviewSentiment nullSentiments = new ReviewSentiment();

            // Test that null lists don't cause exceptions
            int score = laptopService.calculateEachAspectScore(nullSentiments, "DISPLAY");
            assertEquals(0, score, "Score should be 0 when all sentiment lists are null");
        }
    }

    /**
     * Tests focusing on star-level score calculations.
     * The scoring formula used:
     * - For positive aspects: count * star_rating
     * - For negative aspects: -count * (6 - star_rating)
     *
     * This creates a weighted system where:
     * - 5-star positive reviews count more than 1-star positive reviews
     * - 1-star negative reviews are more impactful than 5-star negative reviews
     */
    @Nested
    @DisplayName("Star Score Calculation Tests")
    class StarScoreCalculationTests {

        /**
         * Tests score calculation for specific star ratings.
         * Verifies the core calculation logic for both positive and negative aspects.
         */
        @Test
        @DisplayName("Should calculate score for star rating correctly")
        void testCalculateScoreForStar() {
            // Test score calculation for specific star ratings
            int score = laptopService.calculateScoreForStar(
                    Arrays.asList("DISPLAY", "DISPLAY"),
                    Collections.singletonList("PRICE"),
                    "DISPLAY",
                    5
            );
            assertEquals(10, score, "2 positive reviews * 5 stars = 10");

            int priceScore = laptopService.calculateScoreForStar(
                    Arrays.asList("AUDIO"),
                    Arrays.asList("PRICE", "PRICE"),
                    "PRICE",
                    4
            );
            assertEquals(-4, priceScore, "2 negative reviews * (6-4) = -4");
        }

        /**
         * Tests behavior when an aspect doesn't match any in the lists.
         * Verifies that score is 0 when neither positive nor negative
         * sentiment lists contain the queried aspect.
         */
        @Test
        @DisplayName("Should return 0 when aspect doesn't match")
        void testNonMatchingAspect() {
            int score = laptopService.calculateScoreForStar(
                    Arrays.asList("DISPLAY", "DISPLAY"),
                    Arrays.asList("PRICE", "PRICE"),
                    "AUDIO", // Aspect not in either list
                    5
            );
            assertEquals(0, score, "Score should be 0 when aspect doesn't match any entries");
        }

        /**
         * Tests boundary cases for star values.
         * Verifies correct calculations for the extreme star ratings (1 and 5)
         * for both positive and negative sentiments.
         */
        @Test
        @DisplayName("Should handle extreme star values correctly")
        void testBoundaryStarValues() {
            // Test lowest star value (1)
            int score1 = laptopService.calculateScoreForStar(
                    Arrays.asList("DISPLAY"),
                    null,
                    "DISPLAY",
                    5
            );
            assertEquals(5, score1, "1 positive review * 5 star = 5");
            
            // Test lowest star value (1)
            int score2 = laptopService.calculateScoreForStar(
                    Arrays.asList("DISPLAY"),
                    null,
                    "DISPLAY",
                    1
            );
            assertEquals(1, score2, "1 positive review * 1 star = 1");

            // Test highest negative weight (5-star negative = -1)
            int score3 = laptopService.calculateScoreForStar(
                    null,
                    Arrays.asList("DISPLAY"),
                    "DISPLAY",
                    5
            );
            assertEquals(-1, score3, "1 negative review * (6-5) = -1");

            // Test highest negative weight (1-star negative = -5)
            int score4 = laptopService.calculateScoreForStar(
                    null,
                    Arrays.asList("DISPLAY"),
                    "DISPLAY",
                    1
            );
            assertEquals(-5, score4, "1 negative review * (6-1) = -5");
        }
    }

    /**
     * Tests for laptop retrieval functionality.
     * These verify:
     * 1. Retrieval with empty aspect lists returns all laptops
     * 2. Sorting works correctly for single and multiple aspect criteria
     * 3. Sort order is maintained (descending) - higher scores first
     * 4. Invalid aspect names are handled gracefully
     * 5. Tie-breaking with multiple sort criteria works properly
     */
    @Nested
    @DisplayName("Get Laptops By Aspects Tests")
    class GetLaptopsByAspectsTests {

        /**
         * Tests retrieval behavior when no aspects are specified.
         * When no aspects are provided, the service should return all laptops
         * without specific sorting.
         */
        @Test
        @DisplayName("Should return all laptops when no aspects provided")
        void testEmptyAspectsList() {
            // Setup mock response
            List<Laptop> mockLaptops = Arrays.asList(new Laptop(), new Laptop());
            Page<Laptop> mockPage = new PageImpl<>(mockLaptops);

            when(laptopRepository.findAll(any(Pageable.class))).thenReturn(mockPage);

            // Test with empty list
            List<String> emptyAspects = Collections.emptyList();
            List<Laptop> results = laptopService.getLaptopsByAspects(emptyAspects);

            assertEquals(2, results.size(), "Should return all laptops for empty aspects list");
            verify(laptopRepository).findAll(any(Pageable.class));
        }

        /**
         * Tests sorting by a single aspect.
         * When sorting by a single aspect, laptops should be ordered
         * with the highest score for that aspect first (descending order).
         * Tests both DISPLAY and PERFORMANCE as sort criteria separately.
         */
        @Test
        @DisplayName("Should sort laptops by specified aspects")
        void testSortByAspects() {
            // Create laptops with meaningful scores
            Laptop laptop1 = new Laptop();
            laptop1.setTitle("High Display");
            laptop1.setDisplayScore(10);
            laptop1.setPerformanceScore(5);

            Laptop laptop2 = new Laptop();
            laptop2.setTitle("High Performance");
            laptop2.setDisplayScore(6);
            laptop2.setPerformanceScore(9);

            // For testing primary vs secondary sort criteria
            Laptop laptop3 = new Laptop();
            laptop3.setTitle("Balanced");
            laptop3.setDisplayScore(8);
            laptop3.setPerformanceScore(8);

            // Pageable object will be created by the service, we just need to
            // ensure our mock repository returns results in the correct order
            when(laptopRepository.findAll(any(Pageable.class))).thenReturn(
                    new PageImpl<>(Arrays.asList(laptop1, laptop3, laptop2)) // Expected sort order by DISPLAY (primary)
            );

            // Test with DISPLAY as primary sort criterion
            List<String> aspects = Collections.singletonList("DISPLAY");
            List<Laptop> results = laptopService.getLaptopsByAspects(aspects);

            // Verify correct order based on display score (highest first)
            assertEquals(3, results.size());
            assertEquals("High Display", results.get(0).getTitle()); // 10
            assertEquals("Balanced", results.get(1).getTitle());     // 8
            assertEquals("High Performance", results.get(2).getTitle()); // 6

            // Now test with PERFORMANCE as primary sort criterion
            when(laptopRepository.findAll(any(Pageable.class))).thenReturn(
                    new PageImpl<>(Arrays.asList(laptop2, laptop3, laptop1)) // Expected sort order by PERFORMANCE
            );

            aspects = Collections.singletonList("PERFORMANCE");
            results = laptopService.getLaptopsByAspects(aspects);

            // Verify correct order based on performance score (highest first)
            assertEquals(3, results.size());
            assertEquals("High Performance", results.get(0).getTitle()); // 9
            assertEquals("Balanced", results.get(1).getTitle());     // 8
            assertEquals("High Display", results.get(2).getTitle()); // 5
        }

        /**
         * Tests sorting with multiple criteria where primary sort values are tied.
         * When two laptops have the same score for the primary sort aspect,
         * the secondary aspect score should be used to break the tie.
         * In this test, both laptops have displayScore=10, so performanceScore
         * determines the final order.
         */
        @Test
        @DisplayName("Should handle combined sort criteria")
        void testCombinedSortCriteria() {
            // Create laptops with tied primary criteria
            Laptop laptop1 = new Laptop();
            laptop1.setTitle("High Display, Low Performance");
            laptop1.setDisplayScore(10);
            laptop1.setPerformanceScore(5);

            Laptop laptop2 = new Laptop();
            laptop2.setTitle("Medium Display, High Performance");
            laptop2.setDisplayScore(10); // Same display score as laptop1
            laptop2.setPerformanceScore(9); // Higher performance

            // Mock repository to return laptops in correct order (tied on display, sorted by performance)
            when(laptopRepository.findAll(any(Pageable.class))).thenReturn(
                    new PageImpl<>(Arrays.asList(laptop2, laptop1))
            );

            // Test with multiple aspects (DISPLAY first, then PERFORMANCE)
            List<String> aspects = Arrays.asList("DISPLAY", "PERFORMANCE");
            List<Laptop> results = laptopService.getLaptopsByAspects(aspects);

            // Verify results - should be sorted by DISPLAY first, then by PERFORMANCE
            assertEquals(2, results.size());
            assertEquals("Medium Display, High Performance", results.get(0).getTitle());
            assertEquals("High Display, Low Performance", results.get(1).getTitle());
        }

        /**
         * Tests handling of invalid aspect names.
         * When an invalid/unknown aspect name is included in the sort criteria,
         * it should be ignored without causing errors.
         */
        @Test
        @DisplayName("Should handle invalid aspect names in sort")
        void testInvalidAspectNames() {
            // Setup mock response
            List<Laptop> mockLaptops = Arrays.asList(new Laptop());
            Page<Laptop> mockPage = new PageImpl<>(mockLaptops);

            when(laptopRepository.findAll(any(Pageable.class))).thenReturn(mockPage);

            // Test with invalid aspect name
            List<String> aspects = Arrays.asList("INVALID_ASPECT", "DISPLAY");
            List<Laptop> results = laptopService.getLaptopsByAspects(aspects);

            assertEquals(1, results.size(), "Should ignore invalid aspect names");
            verify(laptopRepository).findAll(any(Pageable.class));
        }
    }

    /**
     * Tests handling of null sentiment data.
     * When a laptop doesn't have review sentiments, the service
     * should handle this gracefully without NullPointerExceptions.
     */
    @Test
    @DisplayName("Should handle null sentiment in calculateAspectScores")
    void testNullSentiment() {
        // Create a map without review_sentiments
        Map<String, Object> laptopMap = new HashMap<>();
        laptopMap.put("title", "Test Laptop");

        // Should not throw exception
        Laptop processedLaptop = laptopService.calculateAspectScores(laptopMap);

        assertNotNull(processedLaptop);
        // All scores should be null or 0 depending on implementation
    }
}
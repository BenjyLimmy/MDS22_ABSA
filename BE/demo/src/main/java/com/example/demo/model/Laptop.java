package com.example.demo.model;

import java.util.List;
import java.util.Map;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;


@Document(collection = "laptops")
@JsonIgnoreProperties(ignoreUnknown = true)
public class Laptop {
    @Id
    private String id; // MongoDB will automatically generate an _id

    @JsonProperty("title")
    private String title;

    @JsonProperty("product_id")
    private String productId;

    @JsonProperty("price")
    private String price;

    @JsonProperty("image_url")
    private String imageUrl;

    @JsonProperty("product_url")
    private String productUrl;

    @JsonProperty("average_rating")
    private String averageRating;

    @JsonProperty("review_count")
    private String reviewCount; 

    @JsonProperty("histogram")
    private Map<String, String> histogram;

    @JsonProperty("histogram_reviews_to_scrape")
    private Map<String, String> histogramReviewsToScrape;

    @JsonProperty("review")
    private List<Review> review;

    @JsonProperty("review_summary")
    private String reviewSummary;

    @JsonProperty("review_sentiments")
    private ReviewSentiment reviewSentiments;

    private Integer audioScore;
    private Integer batteryScore;
    private Integer buildQualityScore;
    private Integer designScore;
    private Integer displayScore;
    private Integer performanceScore;
    private Integer portabilityScore;
    private Integer priceScore;


    // Getters and Setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getProductId() {
        return productId;
    }

    public void setProductId(String productId) {
        this.productId = productId;
    }

    public String getPrice() {
        return price;
    }

    public void setPrice(String price) {
        this.price = price;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public String getProductUrl() {
        return productUrl;
    }

    public void setProductUrl(String productUrl) {
        this.productUrl = productUrl;
    }

    public String getAverageRating() {
        return averageRating;
    }

    public void setAverageRating(String averageRating) {
        this.averageRating = averageRating;
    }

    public String getReviewCount() {
        return reviewCount;
    }

    public void setReviewCount(String reviewCount) {
        this.reviewCount = reviewCount;
    }

    public Map<String, String> getHistogram() {
        return histogram;
    }

    public void setHistogram(Map<String, String> histogram) {
        this.histogram = histogram;
    }

    public Map<String, String> getHistogramReviewsToScrape() {
        return histogramReviewsToScrape;
    }

    public void setHistogramReviewsToScrape(Map<String, String> histogramReviewsToScrape) {
        this.histogramReviewsToScrape = histogramReviewsToScrape;
    }

    public List<Review> getReview() {
        return review;
    }

    public void setReview(List<Review> review) {
        this.review = review;
    }

    public String getReviewSummary() {
        return reviewSummary;
    }

    public void setReviewSummary(String reviewSummary) {
        this.reviewSummary = reviewSummary;
    }

    public ReviewSentiment getReviewSentiments() {
        return reviewSentiments;
    }

    public void setReviewSentiments(ReviewSentiment reviewSentiments) {
        this.reviewSentiments = reviewSentiments;
    }

    public Integer getAudioScore() {
        return audioScore;
    }

    public void setAudioScore(Integer audioScore) {
        this.audioScore = audioScore;
    }

    public Integer getBatteryScore() {
        return batteryScore;
    }

    public void setBatteryScore(Integer batteryScore) {
        this.batteryScore = batteryScore;
    }

    public Integer getBuildQualityScore() {
        return buildQualityScore;
    }

    public void setBuildQualityScore(Integer buildQualityScore) {
        this.buildQualityScore = buildQualityScore;
    }

    public Integer getDesignScore() {
        return designScore;
    }

    public void setDesignScore(Integer designScore) {
        this.designScore = designScore;
    }

    public Integer getDisplayScore() {
        return displayScore;
    }

    public void setDisplayScore(Integer displayScore) {
        this.displayScore = displayScore;
    }

    public Integer getPerformanceScore() {
        return performanceScore;
    }

    public void setPerformanceScore(Integer performanceScore) {
        this.performanceScore = performanceScore;
    }

    public Integer getPortabilityScore() {
        return portabilityScore;
    }

    public void setPortabilityScore(Integer portabilityScore) {
        this.portabilityScore = portabilityScore;
    }

    public Integer getPriceScore() {
        return priceScore;
    }

    public void setPriceScore(Integer priceScore) {
        this.priceScore = priceScore;
    }

    



}

package com.example.demo.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
public class Review {
    @JsonProperty("review_text")
    private String reviewText;

    public String getReviewText() {
        return reviewText;
    }

    public void setReviewText(String reviewText) {
        this.reviewText = reviewText;
    }
    
}

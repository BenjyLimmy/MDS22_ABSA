package com.example.demo.model;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
public class ReviewSentiment {
    @JsonProperty("pos_5_aspects")
    private List<String> pos5Aspects;

    @JsonProperty("neg_5_aspects")
    private List<String> neg5Aspects;

    @JsonProperty("pos_4_aspects")
    private List<String> pos4Aspects;

    @JsonProperty("neg_4_aspects")
    private List<String> neg4Aspects;

    @JsonProperty("pos_3_aspects")
    private List<String> pos3Aspects;

    @JsonProperty("neg_3_aspects")
    private List<String> neg3Aspects;

    @JsonProperty("pos_2_aspects")
    private List<String> pos2Aspects;

    @JsonProperty("neg_2_aspects")
    private List<String> neg2Aspects;

    @JsonProperty("pos_1_aspects")
    private List<String> pos1Aspects;

    @JsonProperty("neg_1_aspects")
    private List<String> neg1Aspects;
    

    public List<String> getPos5Aspects() {
        return pos5Aspects;
    }

    public void setPos5Aspects(List<String> pos5Aspects) {
        this.pos5Aspects = pos5Aspects;
    }

    public List<String> getNeg5Aspects() {
        return neg5Aspects;
    }

    public void setNeg5Aspects(List<String> neg5Aspects) {
        this.neg5Aspects = neg5Aspects;
    }

    public List<String> getPos4Aspects() {
        return pos4Aspects;
    }

    public void setPos4Aspects(List<String> pos4Aspects) {
        this.pos4Aspects = pos4Aspects;
    }

    public List<String> getNeg4Aspects() {
        return neg4Aspects;
    }

    public void setNeg4Aspects(List<String> neg4Aspects) {
        this.neg4Aspects = neg4Aspects;
    }

    public List<String> getPos3Aspects() {
        return pos3Aspects;
    }

    public void setPos3Aspects(List<String> pos3Aspects) {
        this.pos3Aspects = pos3Aspects;
    }

    public List<String> getNeg3Aspects() {
        return neg3Aspects;
    }

    public void setNeg3Aspects(List<String> neg3Aspects) {
        this.neg3Aspects = neg3Aspects;
    }

    public List<String> getPos2Aspects() {
        return pos2Aspects;
    }

    public void setPos2Aspects(List<String> pos2Aspects) {
        this.pos2Aspects = pos2Aspects;
    }

    public List<String> getNeg2Aspects() {
        return neg2Aspects;
    }

    public void setNeg2Aspects(List<String> neg2Aspects) {
        this.neg2Aspects = neg2Aspects;
    }

    public List<String> getPos1Aspects() {
        return pos1Aspects;
    }

    public void setPos1Aspects(List<String> pos1Aspects) {
        this.pos1Aspects = pos1Aspects;
    }

    public List<String> getNeg1Aspects() {
        return neg1Aspects;
    }

    public void setNeg1Aspects(List<String> neg1Aspects) {
        this.neg1Aspects = neg1Aspects;
    }
}

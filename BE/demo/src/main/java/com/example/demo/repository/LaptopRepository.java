package com.example.demo.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.model.Laptop;

@Repository
public interface LaptopRepository extends MongoRepository<Laptop, String> {
    // to perform CRUD operations on the laptop collection in MongoDB
}

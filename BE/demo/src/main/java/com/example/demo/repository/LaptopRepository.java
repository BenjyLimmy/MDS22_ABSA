package com.example.demo.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.model.Laptop;
import java.util.Optional;

@Repository
public interface LaptopRepository extends MongoRepository<Laptop, String> {
    // to perform CRUD operations on the laptop collection in MongoDB
    // Find a laptop by its product_id
    Optional<Laptop> findByProductId(String productId);
}

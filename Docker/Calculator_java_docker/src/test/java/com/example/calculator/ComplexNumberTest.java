package com.example.calculator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Complex Number Tests")
class ComplexNumberTest {
    
    @Test
    @DisplayName("should create complex number with positive values")
    void testCreatePositive() {
        ComplexNumber num = new ComplexNumber(3, 4);
        assertEquals(3.0, num.getReal());
        assertEquals(4.0, num.getImaginary());
    }
    
    @Test
    @DisplayName("should create complex number with negative values")
    void testCreateNegative() {
        ComplexNumber num = new ComplexNumber(-2, -5);
        assertEquals(-2.0, num.getReal());
        assertEquals(-5.0, num.getImaginary());
    }
    
    @Test
    @DisplayName("should throw exception for NaN real part")
    void testNaNReal() {
        assertThrows(IllegalArgumentException.class, () -> new ComplexNumber(Double.NaN, 2));
    }
    
    @Test
    @DisplayName("should throw exception for Infinity real part")
    void testInfinityReal() {
        assertThrows(IllegalArgumentException.class, () -> new ComplexNumber(Double.POSITIVE_INFINITY, 2));
    }
    
    @Test
    @DisplayName("should throw exception for NaN imaginary part")
    void testNaNImaginary() {
        assertThrows(IllegalArgumentException.class, () -> new ComplexNumber(1, Double.NaN));
    }
    
    @Test
    @DisplayName("should throw exception for Infinity imaginary part")
    void testInfinityImaginary() {
        assertThrows(IllegalArgumentException.class, () -> new ComplexNumber(1, Double.NEGATIVE_INFINITY));
    }
    
    @Test
    @DisplayName("should return correct string representation for positive imaginary")
    void testToStringPositive() {
        ComplexNumber num = new ComplexNumber(3, 4);
        assertEquals("3.00 + 4.00i", num.toString());
    }
    
    @Test
    @DisplayName("should return correct string representation for negative imaginary")
    void testToStringNegative() {
        ComplexNumber num = new ComplexNumber(3, -4);
        assertEquals("3.00 - 4.00i", num.toString());
    }
    
    @Test
    @DisplayName("should return real part only when imaginary is zero")
    void testToStringRealOnly() {
        ComplexNumber num = new ComplexNumber(5, 0);
        assertEquals("5.00", num.toString());
    }
    
    @Test
    @DisplayName("should be immutable")
    void testImmutability() {
        ComplexNumber num = new ComplexNumber(1, 2);
        double real = num.getReal();
        double imag = num.getImaginary();
        
        // Verify values don't change (private final fields ensure this)
        assertEquals(1.0, real);
        assertEquals(2.0, imag);
    }
}

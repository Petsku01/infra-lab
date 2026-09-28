package com.example.calculator;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Parameterized tests for ComplexNumber operations
 * @author pk
 */
@DisplayName("ComplexNumber Parameterized Tests")
class ComplexNumberParameterizedTest {
    
    @ParameterizedTest
    @CsvSource({
        "3.0, 4.0, 5.0",
        "0.0, 0.0, 0.0",
        "5.0, 0.0, 5.0",
        "0.0, 12.0, 12.0",
        "-3.0, 4.0, 5.0",
        "3.0, -4.0, 5.0"
    })
    @DisplayName("should calculate correct modulus for various inputs")
    void testModulus(double real, double imag, double expectedModulus) {
        ComplexCalculatorService calc = new ComplexCalculatorService();
        ComplexNumber num = new ComplexNumber(real, imag);
        double result = calc.modulus(num);
        assertEquals(expectedModulus, result, 0.0001);
    }
    
    @ParameterizedTest
    @CsvSource({
        "3.0, 4.0, '3.00 + 4.00i'",
        "3.0, -4.0, '3.00 - 4.00i'",
        "5.0, 0.0, '5.00'",
        "0.0, 0.0, '0.00'",
        "-2.5, 3.7, '-2.50 + 3.70i'"
    })
    @DisplayName("should format toString correctly for various inputs")
    void testToString(double real, double imag, String expected) {
        ComplexNumber num = new ComplexNumber(real, imag);
        assertEquals(expected, num.toString());
    }
    
    @ParameterizedTest
    @ValueSource(doubles = {Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY})
    @DisplayName("should reject NaN and infinity in real part")
    void testInvalidRealPart(double invalidValue) {
        assertThrows(IllegalArgumentException.class, 
            () -> new ComplexNumber(invalidValue, 0));
    }
    
    @ParameterizedTest
    @ValueSource(doubles = {Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY})
    @DisplayName("should reject NaN and infinity in imaginary part")
    void testInvalidImaginaryPart(double invalidValue) {
        assertThrows(IllegalArgumentException.class, 
            () -> new ComplexNumber(0, invalidValue));
    }
    
    @ParameterizedTest
    @CsvSource({
        "1.0, 2.0, 3.0, 4.0, 4.0, 6.0",
        "0.0, 0.0, 0.0, 0.0, 0.0, 0.0",
        "-1.0, -2.0, 1.0, 2.0, 0.0, 0.0",
        "5.5, 3.2, 2.1, 1.8, 7.6, 5.0"
    })
    @DisplayName("should add complex numbers correctly")
    void testAddition(double r1, double i1, double r2, double i2, double expectedReal, double expectedImag) {
        ComplexCalculatorService calc = new ComplexCalculatorService();
        ComplexNumber a = new ComplexNumber(r1, i1);
        ComplexNumber b = new ComplexNumber(r2, i2);
        ComplexNumber result = calc.add(a, b);
        assertEquals(expectedReal, result.getReal(), 0.0001);
        assertEquals(expectedImag, result.getImaginary(), 0.0001);
    }
}

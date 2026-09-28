package com.example.calculator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ComplexCalculatorServiceTest {
    
    private ComplexCalculatorService calc;
    
    @BeforeEach
    void setUp() {
        calc = new ComplexCalculatorService();
    }
    
    @Test
    void add() {
        ComplexNumber result = calc.add(new ComplexNumber(3, 4), new ComplexNumber(1, 2));
        assertEquals(4.0, result.getReal());
        assertEquals(6.0, result.getImaginary());
    }
    
    @Test
    void subtract() {
        ComplexNumber result = calc.subtract(new ComplexNumber(5, 7), new ComplexNumber(2, 3));
        assertEquals(3.0, result.getReal());
        assertEquals(4.0, result.getImaginary());
    }
    
    @Test
    void multiply() {
        ComplexNumber result = calc.multiply(new ComplexNumber(2, 3), new ComplexNumber(1, -1));
        assertEquals(5.0, result.getReal());
        assertEquals(1.0, result.getImaginary());
    }
    
    @Test
    void divide() {
        ComplexNumber result = calc.divide(new ComplexNumber(1, 2), new ComplexNumber(1, 1));
        assertEquals(1.5, result.getReal(), 0.0001);
        assertEquals(0.5, result.getImaginary(), 0.0001);
    }
    
    @Test
    void modulus() {
        double result = calc.modulus(new ComplexNumber(3, 4));
        assertEquals(5.0, result);
    }
    
    @Test
    void divideByZero() {
        assertThrows(ArithmeticException.class, 
            () -> calc.divide(new ComplexNumber(1, 2), new ComplexNumber(0, 0)));
    }
    
    @Test
    void nullChecks() {
        assertThrows(IllegalArgumentException.class, () -> calc.add(null, new ComplexNumber(1, 2)));
        assertThrows(IllegalArgumentException.class, () -> calc.modulus(null));
    }
}

package com.example.calculator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Extended tests for ComplexCalculatorService edge cases
 * @author pk
 */
class ComplexCalculatorServiceExtendedTest {
    
    private ComplexCalculatorService calc;
    
    @BeforeEach
    void setUp() {
        calc = new ComplexCalculatorService();
    }
    
    @Test
    void testOverflowDetection() {
        ComplexNumber large = new ComplexNumber(Double.MAX_VALUE / 2, Double.MAX_VALUE / 2);
        
        // This should potentially overflow and be caught
        assertThrows(ArithmeticException.class, 
            () -> calc.multiply(large, large));
    }
    
    @Test
    void testUnderflowHandling() {
        ComplexNumber tiny = new ComplexNumber(Double.MIN_VALUE, Double.MIN_VALUE);
        ComplexNumber result = calc.multiply(tiny, tiny);
        
        // Should handle underflow gracefully (might become zero)
        assertNotNull(result);
    }
    
    @Test
    void testDivideByVerySmallNumber() {
        ComplexNumber numerator = new ComplexNumber(1.0, 1.0);
        ComplexNumber denominator = new ComplexNumber(Double.MIN_VALUE, Double.MIN_VALUE);
        
        // Division by very small number might overflow
        assertThrows(ArithmeticException.class, 
            () -> calc.divide(numerator, denominator));
    }
    
    @Test
    void testAdditionCommutative() {
        ComplexNumber a = new ComplexNumber(3.0, 4.0);
        ComplexNumber b = new ComplexNumber(5.0, 6.0);
        
        ComplexNumber result1 = calc.add(a, b);
        ComplexNumber result2 = calc.add(b, a);
        
        assertEquals(result1, result2);
    }
    
    @Test
    void testMultiplicationCommutative() {
        ComplexNumber a = new ComplexNumber(2.0, 3.0);
        ComplexNumber b = new ComplexNumber(4.0, 5.0);
        
        ComplexNumber result1 = calc.multiply(a, b);
        ComplexNumber result2 = calc.multiply(b, a);
        
        assertEquals(result1, result2);
    }
    
    @Test
    void testAdditionAssociative() {
        ComplexNumber a = new ComplexNumber(1.0, 2.0);
        ComplexNumber b = new ComplexNumber(3.0, 4.0);
        ComplexNumber c = new ComplexNumber(5.0, 6.0);
        
        ComplexNumber result1 = calc.add(calc.add(a, b), c);
        ComplexNumber result2 = calc.add(a, calc.add(b, c));
        
        assertEquals(result1.getReal(), result2.getReal(), 0.0001);
        assertEquals(result1.getImaginary(), result2.getImaginary(), 0.0001);
    }
    
    @Test
    void testMultiplicationByZero() {
        ComplexNumber a = new ComplexNumber(3.0, 4.0);
        ComplexNumber zero = new ComplexNumber(0.0, 0.0);
        
        ComplexNumber result = calc.multiply(a, zero);
        
        assertEquals(0.0, result.getReal(), 0.0001);
        assertEquals(0.0, result.getImaginary(), 0.0001);
    }
    
    @Test
    void testMultiplicationByOne() {
        ComplexNumber a = new ComplexNumber(3.0, 4.0);
        ComplexNumber one = new ComplexNumber(1.0, 0.0);
        
        ComplexNumber result = calc.multiply(a, one);
        
        assertEquals(a.getReal(), result.getReal(), 0.0001);
        assertEquals(a.getImaginary(), result.getImaginary(), 0.0001);
    }
    
    @Test
    void testDivisionByOne() {
        ComplexNumber a = new ComplexNumber(3.0, 4.0);
        ComplexNumber one = new ComplexNumber(1.0, 0.0);
        
        ComplexNumber result = calc.divide(a, one);
        
        assertEquals(a.getReal(), result.getReal(), 0.0001);
        assertEquals(a.getImaginary(), result.getImaginary(), 0.0001);
    }
    
    @Test
    void testModulusZero() {
        ComplexNumber zero = new ComplexNumber(0.0, 0.0);
        double result = calc.modulus(zero);
        assertEquals(0.0, result, 0.0001);
    }
    
    @Test
    void testModulusPythagorean() {
        // 3-4-5 Pythagorean triple
        ComplexNumber c = new ComplexNumber(3.0, 4.0);
        double result = calc.modulus(c);
        assertEquals(5.0, result, 0.0001);
    }
    
    @Test
    void testSubtractSelf() {
        ComplexNumber a = new ComplexNumber(3.0, 4.0);
        ComplexNumber result = calc.subtract(a, a);
        
        assertEquals(0.0, result.getReal(), 0.0001);
        assertEquals(0.0, result.getImaginary(), 0.0001);
    }
    
    @Test
    void testDivideSelf() {
        ComplexNumber a = new ComplexNumber(3.0, 4.0);
        ComplexNumber result = calc.divide(a, a);
        
        // Should equal 1 + 0i
        assertEquals(1.0, result.getReal(), 0.0001);
        assertEquals(0.0, result.getImaginary(), 0.0001);
    }
    
    @Test
    void testComplexConjugateMultiplication() {
        ComplexNumber z = new ComplexNumber(3.0, 4.0);
        ComplexNumber conjugate = new ComplexNumber(3.0, -4.0);
        
        ComplexNumber result = calc.multiply(z, conjugate);
        
        // Result should be real: |z|^2
        assertEquals(25.0, result.getReal(), 0.0001);
        assertEquals(0.0, result.getImaginary(), 0.0001);
    }
}

package com.example.calculator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Business logic tests for ComplexCalculatorService.
 * Tests edge cases, error conditions, and business rules.
 * 
 * @author pk
 */
class ComplexCalculatorServiceBusinessTest {
    
    private final ComplexCalculatorService service = new ComplexCalculatorService();
    
    @Test
    @DisplayName("Division by zero should throw ArithmeticException")
    void testDivisionByZero() {
        ComplexNumber a = new ComplexNumber(5, 3);
        ComplexNumber zero = new ComplexNumber(0, 0);
        
        assertThrows(ArithmeticException.class, () -> service.divide(a, zero),
            "Dividing by zero should throw ArithmeticException");
    }
    
    @Test
    @DisplayName("Null parameters should throw IllegalArgumentException")
    void testNullParametersInAdd() {
        ComplexNumber a = new ComplexNumber(1, 2);
        
        assertThrows(IllegalArgumentException.class, () -> service.add(null, a));
        assertThrows(IllegalArgumentException.class, () -> service.add(a, null));
        assertThrows(IllegalArgumentException.class, () -> service.add(null, null));
    }
    
    @Test
    @DisplayName("Null parameter in modulus should throw IllegalArgumentException")
    void testNullParameterInModulus() {
        assertThrows(IllegalArgumentException.class, () -> service.modulus(null),
            "Modulus with null should throw IllegalArgumentException");
    }
    
    @Test
    @DisplayName("Very large numbers should be handled correctly")
    void testVeryLargeNumbers() {
        ComplexNumber large1 = new ComplexNumber(1e100, 1e100);
        ComplexNumber large2 = new ComplexNumber(1e100, 1e100);
        
        // Addition should work
        ComplexNumber sum = service.add(large1, large2);
        assertEquals(2e100, sum.getReal(), 1e95);
        assertEquals(2e100, sum.getImaginary(), 1e95);
        
        // Multiplication might overflow to infinity
        assertThrows(ArithmeticException.class, () -> service.multiply(large1, large2),
            "Multiplication of very large numbers should detect overflow");
    }
    
    @Test
    @DisplayName("Very small numbers should preserve precision")
    void testVerySmallNumbers() {
        ComplexNumber small1 = new ComplexNumber(1e-100, 1e-100);
        ComplexNumber small2 = new ComplexNumber(1e-100, 1e-100);
        
        ComplexNumber sum = service.add(small1, small2);
        assertEquals(2e-100, sum.getReal(), 1e-105);
        assertEquals(2e-100, sum.getImaginary(), 1e-105);
    }
    
    @Test
    @DisplayName("Negative zero should be handled consistently")
    void testNegativeZero() {
        ComplexNumber posZero = new ComplexNumber(0.0, 0.0);
        ComplexNumber negZero = new ComplexNumber(-0.0, -0.0);
        
        ComplexNumber result = service.add(posZero, negZero);
        
        // Result should be zero (implementation dependent on sign)
        assertEquals(0.0, Math.abs(result.getReal()), 1e-10);
        assertEquals(0.0, Math.abs(result.getImaginary()), 1e-10);
    }
    
    @Test
    @DisplayName("Conjugate of conjugate should return original")
    void testConjugateIdempotence() {
        ComplexNumber original = new ComplexNumber(3, 4);
        ComplexNumber conjugate1 = original.conjugate();
        ComplexNumber conjugate2 = conjugate1.conjugate();
        
        assertEquals(original.getReal(), conjugate2.getReal(), 1e-10);
        assertEquals(original.getImaginary(), conjugate2.getImaginary(), 1e-10);
    }
    
    @Test
    @DisplayName("Addition should be commutative")
    void testAdditionCommutative() {
        ComplexNumber a = new ComplexNumber(3, 4);
        ComplexNumber b = new ComplexNumber(1, 2);
        
        ComplexNumber result1 = service.add(a, b);
        ComplexNumber result2 = service.add(b, a);
        
        assertEquals(result1.getReal(), result2.getReal(), 1e-10);
        assertEquals(result1.getImaginary(), result2.getImaginary(), 1e-10);
    }
    
    @Test
    @DisplayName("Multiplication should be commutative")
    void testMultiplicationCommutative() {
        ComplexNumber a = new ComplexNumber(3, 4);
        ComplexNumber b = new ComplexNumber(1, 2);
        
        ComplexNumber result1 = service.multiply(a, b);
        ComplexNumber result2 = service.multiply(b, a);
        
        assertEquals(result1.getReal(), result2.getReal(), 1e-10);
        assertEquals(result1.getImaginary(), result2.getImaginary(), 1e-10);
    }
    
    @Test
    @DisplayName("Subtraction should be anticommutative")
    void testSubtractionAnticommutative() {
        ComplexNumber a = new ComplexNumber(5, 3);
        ComplexNumber b = new ComplexNumber(2, 1);
        
        ComplexNumber result1 = service.subtract(a, b);
        ComplexNumber result2 = service.subtract(b, a);
        
        assertEquals(result1.getReal(), -result2.getReal(), 1e-10);
        assertEquals(result1.getImaginary(), -result2.getImaginary(), 1e-10);
    }
    
    @Test
    @DisplayName("Multiplication by identity should return original")
    void testMultiplicationByIdentity() {
        ComplexNumber a = new ComplexNumber(3, 4);
        ComplexNumber identity = new ComplexNumber(1, 0);
        
        ComplexNumber result = service.multiply(a, identity);
        
        assertEquals(a.getReal(), result.getReal(), 1e-10);
        assertEquals(a.getImaginary(), result.getImaginary(), 1e-10);
    }
    
    @Test
    @DisplayName("Addition with additive inverse should yield zero")
    void testAdditiveInverse() {
        ComplexNumber a = new ComplexNumber(3, 4);
        ComplexNumber negA = new ComplexNumber(-3, -4);
        
        ComplexNumber result = service.add(a, negA);
        
        assertEquals(0.0, result.getReal(), 1e-10);
        assertEquals(0.0, result.getImaginary(), 1e-10);
    }
    
    @Test
    @DisplayName("Modulus of zero should be zero")
    void testModulusOfZero() {
        ComplexNumber zero = new ComplexNumber(0, 0);
        
        double modulus = service.modulus(zero);
        
        assertEquals(0.0, modulus, 1e-10);
    }
    
    @Test
    @DisplayName("Modulus should satisfy triangle inequality")
    void testModulusTriangleInequality() {
        ComplexNumber a = new ComplexNumber(3, 4);
        ComplexNumber b = new ComplexNumber(1, 2);
        ComplexNumber sum = service.add(a, b);
        
        double modA = service.modulus(a);
        double modB = service.modulus(b);
        double modSum = service.modulus(sum);
        
        // |a + b| <= |a| + |b|
        assertTrue(modSum <= modA + modB + 1e-10, 
            "Modulus should satisfy triangle inequality");
    }
    
    @Test
    @DisplayName("Division then multiplication should recover original")
    void testDivisionMultiplicationInverse() {
        ComplexNumber a = new ComplexNumber(5, 3);
        ComplexNumber b = new ComplexNumber(2, 1);
        
        ComplexNumber quotient = service.divide(a, b);
        ComplexNumber recovered = service.multiply(quotient, b);
        
        assertEquals(a.getReal(), recovered.getReal(), 1e-10);
        assertEquals(a.getImaginary(), recovered.getImaginary(), 1e-10);
    }
    
    @Test
    @DisplayName("Modulus should be multiplicative")
    void testModulusMultiplicative() {
        ComplexNumber a = new ComplexNumber(3, 4);
        ComplexNumber b = new ComplexNumber(1, 2);
        ComplexNumber product = service.multiply(a, b);
        
        double modA = service.modulus(a);
        double modB = service.modulus(b);
        double modProduct = service.modulus(product);
        
        assertEquals(modA * modB, modProduct, 1e-10,
            "Modulus should satisfy |ab| = |a||b|");
    }
}

package com.example.calculator;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashSet;
import java.util.Set;

/**
 * Extended tests for ComplexNumber
 * @author pk
 */
class ComplexNumberExtendedTest {
    
    @Test
    void testEqualsReflexive() {
        ComplexNumber c = new ComplexNumber(3.0, 4.0);
        assertEquals(c, c);
    }
    
    @Test
    void testEqualsSymmetric() {
        ComplexNumber c1 = new ComplexNumber(3.0, 4.0);
        ComplexNumber c2 = new ComplexNumber(3.0, 4.0);
        assertEquals(c1, c2);
        assertEquals(c2, c1);
    }
    
    @Test
    void testEqualsTransitive() {
        ComplexNumber c1 = new ComplexNumber(3.0, 4.0);
        ComplexNumber c2 = new ComplexNumber(3.0, 4.0);
        ComplexNumber c3 = new ComplexNumber(3.0, 4.0);
        assertEquals(c1, c2);
        assertEquals(c2, c3);
        assertEquals(c1, c3);
    }
    
    @Test
    void testEqualsNull() {
        ComplexNumber c = new ComplexNumber(3.0, 4.0);
        assertNotEquals(c, null);
    }
    
    @Test
    void testEqualsDifferentClass() {
        ComplexNumber c = new ComplexNumber(3.0, 4.0);
        assertNotEquals(c, "3.0 + 4.0i");
    }
    
    @Test
    void testHashCodeConsistency() {
        ComplexNumber c = new ComplexNumber(3.0, 4.0);
        int hash1 = c.hashCode();
        int hash2 = c.hashCode();
        assertEquals(hash1, hash2);
    }
    
    @Test
    void testHashCodeEqualObjects() {
        ComplexNumber c1 = new ComplexNumber(3.0, 4.0);
        ComplexNumber c2 = new ComplexNumber(3.0, 4.0);
        assertEquals(c1.hashCode(), c2.hashCode());
    }
    
    @Test
    void testHashSetUsage() {
        Set<ComplexNumber> set = new HashSet<>();
        ComplexNumber c1 = new ComplexNumber(3.0, 4.0);
        ComplexNumber c2 = new ComplexNumber(3.0, 4.0);
        
        set.add(c1);
        set.add(c2);
        
        // Should contain only 1 element (they're equal)
        assertEquals(1, set.size());
        assertTrue(set.contains(c1));
        assertTrue(set.contains(c2));
    }
    
    @Test
    void testNegativeZero() {
        ComplexNumber c1 = new ComplexNumber(0.0, -0.0);
        ComplexNumber c2 = new ComplexNumber(-0.0, 0.0);
        // In Java, 0.0 == -0.0, so these should be equal
        assertEquals(c1, c2);
    }
    
    @Test
    void testVerySmallNumbers() {
        ComplexNumber c = new ComplexNumber(Double.MIN_VALUE, Double.MIN_VALUE);
        assertNotNull(c);
        assertEquals(Double.MIN_VALUE, c.getReal());
        assertEquals(Double.MIN_VALUE, c.getImaginary());
    }
    
    @Test
    void testVeryLargeNumbers() {
        double large = Double.MAX_VALUE / 2;
        ComplexNumber c = new ComplexNumber(large, large);
        assertNotNull(c);
        assertEquals(large, c.getReal());
        assertEquals(large, c.getImaginary());
    }
    
    @Test
    void testToStringPrecision() {
        ComplexNumber c = new ComplexNumber(3.14159265, 2.71828182);
        String result = c.toString();
        // Should have 4 decimal places
        assertTrue(result.contains("3.1416"));
        assertTrue(result.contains("2.7183"));
    }
    
    @Test
    void testToStringZeroImaginary() {
        ComplexNumber c = new ComplexNumber(5.1234, 0.0);
        String result = c.toString();
        assertFalse(result.contains("i"));
        assertTrue(result.contains("5.1234"));
    }
    
    @Test
    void testConstructorValidation() {
        assertThrows(IllegalArgumentException.class, 
            () -> new ComplexNumber(Double.NaN, 4.0));
        assertThrows(IllegalArgumentException.class, 
            () -> new ComplexNumber(3.0, Double.NaN));
        assertThrows(IllegalArgumentException.class, 
            () -> new ComplexNumber(Double.POSITIVE_INFINITY, 4.0));
        assertThrows(IllegalArgumentException.class, 
            () -> new ComplexNumber(3.0, Double.NEGATIVE_INFINITY));
    }
}

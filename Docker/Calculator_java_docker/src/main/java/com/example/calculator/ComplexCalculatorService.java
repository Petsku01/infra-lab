/**
 * Service for complex number operations
 * @author pk
 */
package com.example.calculator;

/**
 * Service providing arithmetic operations on complex numbers.
 * All operations validate inputs and results for null, NaN, and infinity.
 */
public class ComplexCalculatorService {

    /**
     * Validates two complex numbers for null values.
     * @param a first complex number
     * @param b second complex number
     * @throws IllegalArgumentException if either parameter is null
     */
    private void validate(ComplexNumber a, ComplexNumber b) {
        if (a == null || b == null) {
            throw new IllegalArgumentException("Complex numbers cannot be null");
        }
    }

    /**
     * Validates a single complex number for null values.
     * @param a complex number to validate
     * @throws IllegalArgumentException if parameter is null
     */
    private void validate(ComplexNumber a) {
        if (a == null) {
            throw new IllegalArgumentException("Complex number cannot be null");
        }
    }

    /**
     * Validates operation result for NaN and infinity.
     * @param real real component of result
     * @param imaginary imaginary component of result
     * @throws ArithmeticException if result is NaN or infinite
     */
    private void validateResult(double real, double imaginary) {
        if (Double.isNaN(real) || Double.isInfinite(real) || 
            Double.isNaN(imaginary) || Double.isInfinite(imaginary)) {
            throw new ArithmeticException("Operation result is NaN or infinite");
        }
    }

    /**
     * Adds two complex numbers.
     * @param a first complex number (must not be null)
     * @param b second complex number (must not be null)
     * @return sum of a and b
     * @throws IllegalArgumentException if a or b is null
     * @throws ArithmeticException if result is NaN or infinite
     */
    public ComplexNumber add(ComplexNumber a, ComplexNumber b) {
        validate(a, b);
        double real = a.getReal() + b.getReal();
        double imaginary = a.getImaginary() + b.getImaginary();
        validateResult(real, imaginary);
        return new ComplexNumber(real, imaginary);
    }

    /**
     * Subtracts the second complex number from the first.
     * @param a first complex number (minuend, must not be null)
     * @param b second complex number (subtrahend, must not be null)
     * @return difference of a minus b
     * @throws IllegalArgumentException if a or b is null
     * @throws ArithmeticException if result is NaN or infinite
     */
    public ComplexNumber subtract(ComplexNumber a, ComplexNumber b) {
        validate(a, b);
        double real = a.getReal() - b.getReal();
        double imaginary = a.getImaginary() - b.getImaginary();
        validateResult(real, imaginary);
        return new ComplexNumber(real, imaginary);
    }

    /**
     * Multiplies two complex numbers using the formula:
     * (a+bi)(c+di) = (ac-bd) + (ad+bc)i
     * @param a first complex number (must not be null)
     * @param b second complex number (must not be null)
     * @return product of a and b
     * @throws IllegalArgumentException if a or b is null
     * @throws ArithmeticException if result is NaN or infinite
     */
    public ComplexNumber multiply(ComplexNumber a, ComplexNumber b) {
        validate(a, b);
        double real = a.getReal() * b.getReal() - a.getImaginary() * b.getImaginary();
        double imaginary = a.getReal() * b.getImaginary() + a.getImaginary() * b.getReal();
        validateResult(real, imaginary);
        return new ComplexNumber(real, imaginary);
    }

    /**
     * Divides the first complex number by the second.
     * Uses the formula: (a+bi)/(c+di) = ((ac+bd) + (bc-ad)i) / (c²+d²)
     * @param a dividend (must not be null)
     * @param b divisor (must not be null and not zero)
     * @return quotient of a divided by b
     * @throws IllegalArgumentException if a or b is null
     * @throws ArithmeticException if b is zero or result is NaN or infinite
     */
    public ComplexNumber divide(ComplexNumber a, ComplexNumber b) {
        validate(a, b);
        double denominator = b.getReal() * b.getReal() + b.getImaginary() * b.getImaginary();
        // Check for division by zero with epsilon comparison for floating point
        if (denominator <= 1e-10) {
            throw new ArithmeticException("Division by zero or near-zero complex number");
        }
        double real = (a.getReal() * b.getReal() + a.getImaginary() * b.getImaginary()) / denominator;
        double imaginary = (a.getImaginary() * b.getReal() - a.getReal() * b.getImaginary()) / denominator;
        validateResult(real, imaginary);
        return new ComplexNumber(real, imaginary);
    }

    /**
     * Calculates the modulus (absolute value) of a complex number.
     * The modulus is the distance from the origin: √(a²+b²)
     * @param a complex number (must not be null)
     * @return modulus of the complex number (always non-negative)
     * @throws IllegalArgumentException if a is null
     * @throws ArithmeticException if result is NaN or infinite
     */
    public double modulus(ComplexNumber a) {
        validate(a);
        double result = Math.sqrt(a.getReal() * a.getReal() + a.getImaginary() * a.getImaginary());
        if (Double.isNaN(result) || Double.isInfinite(result)) {
            throw new ArithmeticException("Modulus result is NaN or infinite");
        }
        return result;
    }
}
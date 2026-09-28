/**
 * Immutable complex number representation with basic arithmetic operations support.
 * A complex number is represented as a + bi where a is the real part and b is the imaginary part.
 * 
 * <p>This class is immutable - all operations return new instances.</p>
 * <p>NaN and infinite values are not permitted and will throw IllegalArgumentException.</p>
 * 
 * @author pk
 */
package com.example.calculator;

/**
 * Represents an immutable complex number with real and imaginary components.
 */
public class ComplexNumber {
    private final double real;
    private final double imaginary;

    /**
     * Constructs a complex number with specified real and imaginary parts.
     * 
     * @param real the real component
     * @param imaginary the imaginary component
     * @throws IllegalArgumentException if either component is NaN or infinite
     */
    public ComplexNumber(double real, double imaginary) {
        if (Double.isNaN(real) || Double.isInfinite(real) || Double.isNaN(imaginary) || Double.isInfinite(imaginary)) {
            throw new IllegalArgumentException("Real or imaginary part cannot be NaN or infinite");
        }
        this.real = real;
        this.imaginary = imaginary;
    }

    /**
     * Returns the real component of this complex number.
     * @return the real part
     */
    public double getReal() {
        return real;
    }

    /**
     * Returns the imaginary component of this complex number.
     * @return the imaginary part
     */
    public double getImaginary() {
        return imaginary;
    }

    /**
     * Returns the complex conjugate of this number.
     * The conjugate of a+bi is a-bi.
     * 
     * @return a new ComplexNumber representing the conjugate
     */
    public ComplexNumber conjugate() {
        return new ComplexNumber(real, -imaginary);
    }

    /**
     * Returns a string representation of this complex number.
     * Format: "a.aa + b.bbi" for positive imaginary, "a.aa - b.bbi" for negative.
     * If imaginary part is zero, returns only the real part: "a.aa"
     * 
     * @return string representation with 2 decimal places
     */
    @Override
    public String toString() {
        if (imaginary == 0) {
            return String.format("%.2f", real);
        }
        if (imaginary > 0) {
            return String.format("%.2f + %.2fi", real, imaginary);
        }
        return String.format("%.2f - %.2fi", real, -imaginary);
    }

    /**
     * Compares this complex number to another object for equality.
     * Two complex numbers are equal if their real and imaginary parts are equal
     * using {@link Double#compare(double, double)}.
     * 
     * @param obj the object to compare with
     * @return true if the objects are equal, false otherwise
     */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        ComplexNumber that = (ComplexNumber) obj;
        return Double.compare(that.real, real) == 0 &&
               Double.compare(that.imaginary, imaginary) == 0;
    }

    /**
     * Returns a hash code for this complex number.
     * The hash code is computed using the bit representations of both components.
     * 
     * @return hash code value for this object
     */
    @Override
    public int hashCode() {
        int result = 17;
        long realBits = Double.doubleToLongBits(real);
        long imaginaryBits = Double.doubleToLongBits(imaginary);
        result = 31 * result + (int)(realBits ^ (realBits >>> 32));
        result = 31 * result + (int)(imaginaryBits ^ (imaginaryBits >>> 32));
        return result;
    }
}
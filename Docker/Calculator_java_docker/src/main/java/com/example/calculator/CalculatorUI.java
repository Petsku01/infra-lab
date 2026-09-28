/**
 * User interface for complex number calculator
 * @author pk
 */
package com.example.calculator;

import java.util.Scanner;

public class CalculatorUI {
    private static final String YES_INPUT = "y";
    private static final int MAX_RETRIES = 5;
    private final ComplexCalculatorService calculator;
    private final Scanner scanner;
    
    public CalculatorUI() {
        this.calculator = new ComplexCalculatorService();
        this.scanner = new Scanner(System.in);
    }
    
    public void run() {
        try {
            displayWelcome();
            mainLoop();
        } finally {
            scanner.close();
        }
    }
    
    private void displayWelcome() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("   Complex Number Calculator v1.0");
        System.out.println("═══════════════════════════════════════════");
        System.out.println();
        System.out.println("Operations: add, subtract, multiply, divide, modulus, conjugate");
        System.out.println("Type 'help' for examples");
        System.out.println("Type 'exit' to quit");
        System.out.println();
    }
    
    private void mainLoop() {
        int retryCount = 0;
        
        while (true) {
            try {
                String input = readInput("Enter first complex number (real imaginary): ");
                
                if (input.equalsIgnoreCase("exit")) {
                    System.out.println("Goodbye!");
                    break;
                }
                
                if (input.equalsIgnoreCase("help")) {
                    displayHelp();
                    continue;
                }
                
                ComplexNumber num1 = parseComplexNumber(input);
                String operation = readInput("Operation (add/subtract/multiply/divide/modulus/conjugate): ").trim().toLowerCase();
                
                if (operation.equals("conjugate")) {
                    ComplexNumber result = num1.conjugate();
                    System.out.printf("Conjugate of %s = %s%n%n", num1, result);
                    retryCount = 0;
                    continue;
                }
                
                if (operation.equals("modulus")) {
                    double result = calculator.modulus(num1);
                    System.out.printf("Modulus of %s = %.4f%n%n", num1, result);
                    retryCount = 0;
                    continue;
                }
                
                String input2 = readInput("Enter second complex number (real imaginary): ");
                ComplexNumber num2 = parseComplexNumber(input2);
                
                String confirm = readInput(String.format("Confirm: %s %s (%s, %s)? (y/n): ", 
                    operation, "of", num1, num2)).trim().toLowerCase();
                
                if (!confirm.equals(YES_INPUT)) {
                    System.out.println("Cancelled.\n");
                    continue;
                }
                
                ComplexNumber result = performOperation(operation, num1, num2);
                System.out.printf("Result: %s%n%n", result);
                retryCount = 0;
                
            } catch (IllegalArgumentException | ArithmeticException e) {
                System.err.printf("Error: %s%n", e.getMessage());
                if (++retryCount >= MAX_RETRIES) {
                    System.err.println("Too many errors. Exiting.");
                    break;
                }
            }
        }
    }
    
    private void displayHelp() {
        System.out.println("""
            
            EXAMPLES:
            ---------
            Add:       3 4 + 1 2  →  (4.00 + 6.00i)
            Subtract:  5 7 - 2 3  →  (3.00 + 4.00i)
            Multiply:  2 3 * 1 -1 →  (5.00 + 1.00i)
            Divide:    1 2 / 1 1  →  (1.50 + 0.50i)
            Modulus:   3 4        →  5.0000
            Conjugate: 3 4        →  (3.00 - 4.00i)
            
            Format: real and imaginary as decimal numbers
            Example: 3.5 -2.1
            
            """);
    }
    
    private String readInput(String prompt) {
        System.out.print(prompt);
        return scanner.nextLine().trim();
    }
    
    private ComplexNumber parseComplexNumber(String input) {
        if (input == null || input.isEmpty()) {
            throw new IllegalArgumentException("Input cannot be empty");
        }
        
        String[] parts = input.split("\\s+");
        if (parts.length != 2) {
            throw new IllegalArgumentException("Format: <real> <imaginary> (e.g., 3.5 2.1)");
        }
        
        try {
            double real = Double.parseDouble(parts[0]);
            double imaginary = Double.parseDouble(parts[1]);
            
            if (Double.isNaN(real) || Double.isNaN(imaginary)) {
                throw new IllegalArgumentException("Numbers cannot be NaN");
            }
            if (Double.isInfinite(real) || Double.isInfinite(imaginary)) {
                throw new IllegalArgumentException("Numbers cannot be infinite");
            }
            
            return new ComplexNumber(real, imaginary);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid number format. Use decimal numbers (e.g., 3.5 2.1)", e);
        }
    }
    
    private ComplexNumber performOperation(String operation, ComplexNumber a, ComplexNumber b) {
        return switch (operation) {
            case "add" -> calculator.add(a, b);
            case "subtract" -> calculator.subtract(a, b);
            case "multiply" -> calculator.multiply(a, b);
            case "divide" -> calculator.divide(a, b);
            default -> throw new IllegalArgumentException("Unknown operation: " + operation);
        };
    }
}

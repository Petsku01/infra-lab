/**
 * Console I/O abstraction for testing
 * @author pk
 */
package com.example.calculator;

public interface ConsoleIO {
    /**
     * Read a line of input from the console.
     * @param prompt The prompt to display to the user
     * @return The user's input as a string
     */
    String readLine(String prompt);
    
    /**
     * Write a line of output to the console.
     * @param message The message to display
     */
    void writeLine(String message);
    
    /**
     * Write formatted output to the console.
     * @param format The format string
     * @param args The arguments for the format string
     */
    void writeFormatted(String format, Object... args);
}

/**
 * System console implementation of ConsoleIO
 * @author pk
 */
package com.example.calculator;

import java.util.Scanner;

public class SystemConsoleIO implements ConsoleIO {
    private final Scanner scanner;
    
    public SystemConsoleIO(Scanner scanner) {
        this.scanner = scanner;
    }
    
    @Override
    public String readLine(String prompt) {
        System.out.print(prompt);
        return scanner.nextLine();
    }
    
    @Override
    public void writeLine(String message) {
        System.out.println(message);
    }
    
    @Override
    public void writeFormatted(String format, Object... args) {
        System.out.printf(format, args);
    }
}

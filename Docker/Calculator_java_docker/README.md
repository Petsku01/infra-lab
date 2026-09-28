# Complex Number Calculator

A command-line calculator for complex number arithmetic operations, built with Java 17 and packaged as a Docker container.

## Overview

This Docker container provides an interactive calculator for complex number operations including addition, subtraction, multiplication, division, modulus calculation, and conjugate computation. Features epsilon-based floating-point comparisons for numerical stability.

## Features

- **Complex Arithmetic**: Addition, subtraction, multiplication, division
- **Advanced Operations**: Modulus (magnitude), conjugate calculation
- **Floating-Point Safety**: Epsilon-based comparisons (1e-10) for division by zero detection
- **Interactive CLI**: User-friendly command-line interface with input validation
- **Batch Operations**: Supports command-line arguments for scripting
- **Error Handling**: Graceful handling of invalid inputs and edge cases

## Architecture

```
Calculator_java_docker/
├── src/
│   ├── main/java/com/example/calculator/
│   │   ├── ComplexCalculatorMain.java      # Entry point
│   │   ├── CalculatorUI.java               # User interface
│   │   ├── ComplexCalculatorService.java   # Core arithmetic operations
│   │   ├── ComplexNumber.java              # Complex number data structure
│   │   ├── ConsoleIO.java                  # I/O interface
│   │   ├── SystemConsoleIO.java            # Standard console implementation
│   │   └── ObservabilityLogger.java        # Logging utilities
│   └── test/java/com/example/calculator/
│       ├── ComplexCalculatorServiceBusinessTest.java
│       └── ComplexCalculatorServiceExtendedTest.java
├── pom.xml                                  # Maven configuration
└── Dockerfile                               # Multi-stage Docker build
```

## Building the Container

```bash
docker build -t complex-calculator:latest ./Calculator_java_docker
```

Build uses multi-stage Docker:
1. **Stage 1 (Builder)**: Maven 3.9.9 + JDK 17 Alpine for compilation
2. **Stage 2 (Runtime)**: JRE 17 Alpine for minimal runtime footprint

## Usage

### Interactive Mode

Start the calculator in interactive mode:

```bash
docker run -it --rm complex-calculator:latest
```

You'll see the interactive prompt:

```
═══════════════════════════════════════════
   Complex Number Calculator v1.0
═══════════════════════════════════════════

Operations: add, subtract, multiply, divide, modulus, conjugate
Type 'help' for examples
Type 'exit' to quit

Enter first complex number (real imaginary):
```

### Example Interactive Session

```
Enter first complex number (real imaginary): 3 4
Enter second complex number (real imaginary): 1 2
Operation (add/subtract/multiply/divide/modulus/conjugate): add

Result: (3.00 + 4.00i) + (1.00 + 2.00i) = (4.00 + 6.00i)
```

### Conjugate Operation

For conjugate operation, only the first number is used:

```
Enter first complex number (real imaginary): 3 4
Operation: conjugate

Conjugate of (3.00 + 4.00i) = (3.00 - 4.00i)
```

## Operations Reference

### Addition
Adds two complex numbers: (a + bi) + (c + di) = (a+c) + (b+d)i

### Subtraction
Subtracts two complex numbers: (a + bi) - (c + di) = (a-c) + (b-d)i

### Multiplication
Multiplies two complex numbers: (a + bi) * (c + di) = (ac-bd) + (ad+bc)i

### Division
Divides two complex numbers with zero-division protection:
(a + bi) / (c + di) = [(ac+bd) + (bc-ad)i] / (c^2 + d^2)

### Modulus
Calculates magnitude: |a + bi| = sqrt(a^2 + b^2)

### Conjugate
Returns the conjugate: conjugate(a + bi) = a - bi

## Input Format

Complex numbers are entered as two space-separated numbers:
- First number: Real part
- Second number: Imaginary part

Examples:
- `3 4` represents 3 + 4i
- `-2 5` represents -2 + 5i
- `0 -1` represents -i
- `7 0` represents 7 (real number)

## Error Handling

The calculator handles various error conditions:

- **Division by Zero**: Detected using epsilon comparison (denominator < 1e-10)
- **Invalid Input**: Non-numeric inputs are caught and reported
- **Empty Input**: Prompts user to retry
- **Overflow**: Java's double precision handles large numbers gracefully

## Examples

### Example 1: Addition
```
Input: (2 + 3i) + (1 + 2i)
Output: (3.00 + 5.00i)
```

### Example 2: Multiplication
```
Input: (2 + 3i) * (1 + 2i)
Output: (-4.00 + 7.00i)
```

### Example 3: Division
```
Input: (4 + 2i) / (1 + 1i)
Output: (3.00 - 1.00i)
```

### Example 4: Modulus
```
Input: |3 + 4i|
Output: 5.00
```

## JVM Configuration

The container runs with optimized JVM settings:

- **G1GC**: Garbage-First garbage collector for low latency
- **MaxRAMPercentage**: 75% memory allocation for container environments
- **UseContainerSupport**: Container-aware resource limits

## Security Features

- Non-root user execution (appuser:appgroup)
- Minimal JRE 17 Alpine base image
- No external network access required
- Isolated filesystem with proper permissions

## Performance

- Startup time: < 1 second
- Memory footprint: ~50-100 MB (JRE + application)
- Arithmetic operations: O(1) complexity
- No external dependencies at runtime

## Testing

The container includes comprehensive test suites:

- **Unit Tests**: 30+ test cases covering all operations
- **Edge Cases**: Zero division, negative numbers, pure real/imaginary
- **Floating-Point**: Epsilon-based precision validation

Run tests during build:

```bash
docker build -t complex-calculator:test ./Calculator_java_docker
```

Skip tests for faster builds:

```bash
docker build -t complex-calculator:latest ./Calculator_java_docker
# Tests are skipped by default via -DskipTests
```

## Help Command

View examples and usage inside the container:

```
Operations: add, subtract, multiply, divide, modulus, conjugate
Type 'help' for examples
Type 'exit' to quit
```

Type `help` at the prompt for detailed examples.

## Container Specifications

- **Base Image**: eclipse-temurin:17-jre-alpine
- **Size**: 252 MB
- **Java Version**: OpenJDK 17 (LTS)
- **Maven**: 3.9.9
- **User**: appuser (non-root)

## Exit Codes

- **0**: Successful execution
- **1**: Error during execution (division by zero, invalid input)

## Troubleshooting

### Issue: Container exits immediately

**Solution**: Use interactive mode with `-it` flag:

```bash
docker run -it --rm complex-calculator:latest
```

### Issue: Input not recognized

**Solution**: Ensure numbers are space-separated (not comma or other delimiter):

```
Correct: 3 4
Incorrect: 3,4 or (3+4i)
```

### Issue: Division by zero error

**Solution**: The calculator uses epsilon comparison (1e-10). Ensure denominator magnitude is not near zero.

## Version

Current version: 1.0.0

## Dependencies

- Java 17 (OpenJDK)
- Maven 3.9.9 (build-time only)
- JUnit 5.11.4 (test-time only)

## License

See project root for license information.

## Contributing

Contributions welcome. Ensure all tests pass and follow Java code conventions (Google Java Style Guide recommended).

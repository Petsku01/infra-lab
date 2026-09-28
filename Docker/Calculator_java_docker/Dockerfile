# syntax=docker/dockerfile:1
# Stage 1: Build with Maven
FROM maven:3.9.9-eclipse-temurin-17-alpine AS builder

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Runtime (minimal)
FROM eclipse-temurin:17-jre-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser:appgroup

WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app/target/calculator.jar .

ENTRYPOINT ["java", "-XX:+UseG1GC", "-XX:MaxRAMPercentage=75.0", "-XX:+UseContainerSupport", "-jar", "/app/calculator.jar"]


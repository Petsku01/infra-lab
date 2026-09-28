package com.example.calculator;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Structured observability logging for Calculator application.
 * Provides JSON-formatted logs with trace IDs and operation metrics.
 * 
 * @author pk
 */
public class ObservabilityLogger {
    
    private final String component;
    private final String traceId;
    private final Map<String, Object> context;
    private static final Map<String, MetricData> metrics = new ConcurrentHashMap<>();
    
    public ObservabilityLogger(String component) {
        this.component = component;
        this.traceId = UUID.randomUUID().toString();
        this.context = new HashMap<>();
    }
    
    public ObservabilityLogger(String component, String traceId) {
        this.component = component;
        this.traceId = traceId;
        this.context = new HashMap<>();
    }
    
    /**
     * Add persistent context to all log messages
     */
    public void addContext(String key, Object value) {
        context.put(key, value);
    }
    
    /**
     * Log info level message with structured data
     */
    public void info(String message, Object... kvPairs) {
        log("INFO", message, kvPairs);
    }
    
    /**
     * Log warning level message with structured data
     */
    public void warning(String message, Object... kvPairs) {
        log("WARNING", message, kvPairs);
    }
    
    /**
     * Log error level message with structured data
     */
    public void error(String message, Object... kvPairs) {
        log("ERROR", message, kvPairs);
    }
    
    /**
     * Log error with exception details
     */
    public void error(String message, Throwable throwable, Object... kvPairs) {
        Map<String, Object> logData = buildLogData("ERROR", message, kvPairs);
        logData.put("error_type", throwable.getClass().getSimpleName());
        logData.put("error_message", throwable.getMessage());
        
        if (throwable.getCause() != null) {
            logData.put("cause", throwable.getCause().getClass().getSimpleName());
        }
        
        System.err.println(toJson(logData));
    }
    
    /**
     * Start timing an operation
     * @return operation ID for tracking
     */
    public String startOperation(String operationName, Object... kvPairs) {
        String operationId = UUID.randomUUID().toString().substring(0, 8);
        long startTime = System.nanoTime();
        
        Map<String, Object> logData = buildLogData("INFO", "Operation started: " + operationName, kvPairs);
        logData.put("operation", operationName);
        logData.put("operation_id", operationId);
        logData.put("status", "started");
        
        System.out.println(toJson(logData));
        
        // Store start time for metrics
        metrics.put(operationId, new MetricData(operationName, startTime));
        
        return operationId;
    }
    
    /**
     * End timing an operation
     */
    public void endOperation(String operationId, boolean success, Object... kvPairs) {
        MetricData metricData = metrics.remove(operationId);
        if (metricData == null) {
            warning("Operation ID not found", "operation_id", operationId);
            return;
        }
        
        long endTime = System.nanoTime();
        double durationMs = (endTime - metricData.startTime) / 1_000_000.0;
        
        String level = success ? "INFO" : "ERROR";
        String message = success ? 
            "Operation completed: " + metricData.operationName :
            "Operation failed: " + metricData.operationName;
        
        Map<String, Object> logData = buildLogData(level, message, kvPairs);
        logData.put("operation", metricData.operationName);
        logData.put("operation_id", operationId);
        logData.put("status", success ? "completed" : "failed");
        logData.put("duration_ms", String.format("%.2f", durationMs));
        
        System.out.println(toJson(logData));
    }
    
    /**
     * Record a metric value
     */
    public void recordMetric(String metricName, double value, Object... kvPairs) {
        Map<String, Object> logData = buildLogData("INFO", "Metric recorded", kvPairs);
        logData.put("metric_name", metricName);
        logData.put("metric_value", value);
        
        System.out.println(toJson(logData));
    }
    
    private void log(String level, String message, Object... kvPairs) {
        Map<String, Object> logData = buildLogData(level, message, kvPairs);
        System.out.println(toJson(logData));
    }
    
    private Map<String, Object> buildLogData(String level, String message, Object... kvPairs) {
        Map<String, Object> logData = new HashMap<>();
        logData.put("timestamp", Instant.now().toString());
        logData.put("level", level);
        logData.put("trace_id", traceId);
        logData.put("component", component);
        logData.put("message", message);
        
        // Add persistent context
        logData.putAll(context);
        
        // Add key-value pairs
        for (int i = 0; i < kvPairs.length; i += 2) {
            if (i + 1 < kvPairs.length) {
                logData.put(String.valueOf(kvPairs[i]), kvPairs[i + 1]);
            }
        }
        
        return logData;
    }
    
    private String toJson(Map<String, Object> data) {
        StringBuilder json = new StringBuilder("{");
        boolean first = true;
        
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            if (!first) {
                json.append(",");
            }
            first = false;
            
            json.append("\"").append(escape(entry.getKey())).append("\":");
            
            Object value = entry.getValue();
            if (value == null) {
                json.append("null");
            } else if (value instanceof Number) {
                json.append(value);
            } else if (value instanceof Boolean) {
                json.append(value);
            } else {
                json.append("\"").append(escape(String.valueOf(value))).append("\"");
            }
        }
        
        json.append("}");
        return json.toString();
    }
    
    private String escape(String str) {
        return str.replace("\\", "\\\\")
                  .replace("\"", "\\\"")
                  .replace("\n", "\\n")
                  .replace("\r", "\\r")
                  .replace("\t", "\\t");
    }
    
    private static class MetricData {
        final String operationName;
        final long startTime;
        
        MetricData(String operationName, long startTime) {
            this.operationName = operationName;
            this.startTime = startTime;
        }
    }
}

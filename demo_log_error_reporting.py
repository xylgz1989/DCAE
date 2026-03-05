#!/usr/bin/env python
"""
Demonstration of the Log Error Reporting functionality for DCAE.
Story 1.10: Log Error Reporting
"""

from src.dcae.log_error_reporting import LogManager, ErrorReporter, setup_logging

def demo_logging_functionality():
    """Demonstrate the logging functionality."""
    print("=== DCAE Log Error Reporting Demo ===\n")

    # Setup logging configuration
    config = {
        'log_level': 'DEBUG',
        'handlers': {
            'console': {'enabled': True, 'format': 'detailed'},
            'file': {
                'enabled': True,
                'path': './logs/demo.log',
                'rotation': {
                    'max_size_mb': 5,
                    'backup_count': 3
                }
            }
        },
        'filters': {
            'sensitive_patterns': [
                r"(api[_-]?key|token|password)\s*[=:]\s*(['\"]?)([^'\"\s]*?)\2",
                r"(Bearer)\s+([a-zA-Z0-9\._-]+)"
            ]
        }
    }

    # Create log manager with configuration
    log_manager = setup_logging(config)

    print("1. Basic logging with different levels:")
    log_manager.log_debug("Debug information for troubleshooting", "DemoApp")
    log_manager.log_info("Application started successfully", "DemoApp")
    log_manager.log_warning("This is a warning message", "DemoApp")
    log_manager.log_error("An error occurred", "DemoApp", {"error_code": 500, "user_id": 12345})

    print("\n2. Context-rich logging:")
    log_manager.log_info("User login attempt", "AuthModule", {
        "user_id": 98765,
        "ip_address": "192.168.1.100",
        "login_method": "oauth"
    })

    print("\n3. Testing sensitive data filtering:")
    log_manager.log_info("API_KEY = abcd1234efgh5678ijkl9012", "DemoApp")
    log_manager.log_info("Bearer abcdefg123456", "DemoApp")

    print("\n4. Correlation ID support:")
    log_manager.set_correlation_id("corr-12345-xyz")
    log_manager.log_info("Processing request step 1", "RequestProcessor")
    log_manager.log_info("Processing request step 2", "RequestProcessor")

    print("\n5. Error reporting functionality:")
    error_reporter = ErrorReporter(log_manager)

    # Simulate and report an error
    try:
        # Simulate an error
        raise ValueError("Invalid user input: email format is incorrect")
    except ValueError as e:
        error_context = {
            "user_id": 54321,
            "input_field": "email",
            "input_value": "invalid-email",
            "request_id": "req-abc-123"
        }

        # Report the error
        error_report = error_reporter.log_error(
            e,
            "ValidationModule",
            error_context,
            include_traceback=True
        )

        print(f"   Error reported: {error_report['error_type']}")
        print(f"   Error message: {error_report['error_message']}")

    print("\n6. Error classification:")
    print(f"   ValueError classification: {error_reporter.classify_error(ValueError('test'))}")
    print(f"   RuntimeError classification: {error_reporter.classify_error(RuntimeError('test'))}")
    print(f"   ConnectionError classification: {error_reporter.classify_error(ConnectionError('test'))}")

    print("\n=== Demo completed ===")
    print("Check ./logs/demo.log for file output")
    print("Check ./logs/errors.log for error-specific logs")


if __name__ == "__main__":
    demo_logging_functionality()
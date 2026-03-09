"""
Shared Logging Utilities
Logging configuration for all services
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def setup_logger(
    name: str,
    level: str = "INFO",
    json_format: bool = False
) -> logging.Logger:
    """
    Setup logger with consistent configuration

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)

    if json_format:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def log_ai_request(
    logger: logging.Logger,
    task_type: str,
    user_id: int | None,
    prompt_length: int,
    metadata: Dict[str, Any] = None
):
    """Log AI request with structured data"""
    logger.info(
        "AI request initiated",
        extra={
            "task_type": task_type,
            "user_id": user_id,
            "prompt_length": prompt_length,
            "metadata": metadata or {}
        }
    )


def log_ai_response(
    logger: logging.Logger,
    task_type: str,
    user_id: int | None,
    success: bool,
    latency_ms: float,
    tokens_used: int = 0,
    error: str | None = None
):
    """Log AI response with structured data"""
    log_data = {
        "task_type": task_type,
        "user_id": user_id,
        "success": success,
        "latency_ms": latency_ms,
        "tokens_used": tokens_used
    }

    if error:
        logger.error(f"AI request failed: {error}", extra=log_data)
    else:
        logger.info("AI request completed", extra=log_data)


def log_websocket_event(
    logger: logging.Logger,
    event_type: str,
    user_id: int | None,
    room_id: int | None = None,
    metadata: Dict[str, Any] = None
):
    """Log WebSocket events"""
    logger.info(
        f"WebSocket event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "room_id": room_id,
            "metadata": metadata or {}
        }
    )

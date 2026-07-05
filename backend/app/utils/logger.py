import logging
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict

class StructuredJSONFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs logs in a clean structured JSON format,
    ideal for production monitoring and log management tools.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Capture trace/context attributes if present on the record
        for attr in ["request_id", "user_id", "analysis_id", "processing_time_ms"]:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)
                
        # Capture stack traces in case of errors
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging(log_level_str: str = "INFO", environment: str = "development") -> None:
    """
    Configures the root logger. Prints colored text in development for high readability
    and structured JSON in production environment.
    """
    level = getattr(logging, log_level_str.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if environment == "production":
        formatter = StructuredJSONFormatter()
    else:
        # High readability color-coded/formatted console log for development
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Prevent duplicate logs from propagation
    logging.getLogger("uvicorn.access").propagate = False

"""
Logging utilities for the agent framework.

This module provides utilities for logging and debugging.
"""
import logging
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union, List


class AgentLogger:
    """
    Logger for the agent framework.
    
    This class provides a configurable logger with support for console and file output,
    as well as structured logging for easier analysis.
    """
    
    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        console_output: bool = True,
        file_output: bool = False,
        log_dir: str = "logs",
        structured: bool = False
    ):
        """
        Initialize the logger.
        
        Args:
            name: The name of the logger
            level: The logging level
            console_output: Whether to output logs to the console
            file_output: Whether to output logs to a file
            log_dir: The directory to store log files
            structured: Whether to use structured logging (JSON format)
        """
        self.name = name
        self.level = level
        self.console_output = console_output
        self.file_output = file_output
        self.log_dir = log_dir
        self.structured = structured
        
        # Create the logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            if structured:
                formatter = logging.Formatter('%(message)s')
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler if requested
        if file_output:
            # Create log directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Create a log file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            
            if structured:
                formatter = logging.Formatter('%(message)s')
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _format_structured(
        self, 
        level: str, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a structured log message.
        
        Args:
            level: The log level
            message: The log message
            data: Additional data to include in the log
            
        Returns:
            A JSON-formatted string
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "name": self.name,
            "message": message
        }
        
        if data:
            log_entry["data"] = data
        
        return json.dumps(log_entry)
    
    def debug(
        self, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a debug message.
        
        Args:
            message: The log message
            data: Additional data to include in the log
        """
        if self.structured and data:
            self.logger.debug(self._format_structured("DEBUG", message, data))
        else:
            self.logger.debug(message)
    
    def info(
        self, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an info message.
        
        Args:
            message: The log message
            data: Additional data to include in the log
        """
        if self.structured and data:
            self.logger.info(self._format_structured("INFO", message, data))
        else:
            self.logger.info(message)
    
    def warning(
        self, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a warning message.
        
        Args:
            message: The log message
            data: Additional data to include in the log
        """
        if self.structured and data:
            self.logger.warning(self._format_structured("WARNING", message, data))
        else:
            self.logger.warning(message)
    
    def error(
        self, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error message.
        
        Args:
            message: The log message
            data: Additional data to include in the log
        """
        if self.structured and data:
            self.logger.error(self._format_structured("ERROR", message, data))
        else:
            self.logger.error(message)
    
    def critical(
        self, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a critical message.
        
        Args:
            message: The log message
            data: Additional data to include in the log
        """
        if self.structured and data:
            self.logger.critical(self._format_structured("CRITICAL", message, data))
        else:
            self.logger.critical(message)
    
    def log(
        self, 
        level: int, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a message at the specified level.
        
        Args:
            level: The log level
            message: The log message
            data: Additional data to include in the log
        """
        level_name = logging.getLevelName(level)
        if self.structured and data:
            self.logger.log(level, self._format_structured(level_name, message, data))
        else:
            self.logger.log(level, message)


class LogCapture:
    """
    Capture logs for later retrieval.
    
    This class provides a way to capture logs in memory for later retrieval,
    which can be useful for debugging or for returning logs to the user.
    """
    
    def __init__(self, logger_name: str, level: int = logging.DEBUG):
        """
        Initialize the log capture.
        
        Args:
            logger_name: The name of the logger to capture
            level: The minimum logging level to capture
        """
        self.logger_name = logger_name
        self.level = level
        self.logs: List[Dict[str, Any]] = []
        self.handler = None
    
    def start(self) -> None:
        """Start capturing logs."""
        logger = logging.getLogger(self.logger_name)
        
        class CaptureHandler(logging.Handler):
            def __init__(self, capture):
                super().__init__()
                self.capture = capture
            
            def emit(self, record):
                self.capture.logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": record.levelname,
                    "name": record.name,
                    "message": record.getMessage()
                })
        
        self.handler = CaptureHandler(self)
        self.handler.setLevel(self.level)
        logger.addHandler(self.handler)
    
    def stop(self) -> None:
        """Stop capturing logs."""
        if self.handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self.handler)
            self.handler = None
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Get the captured logs.
        
        Returns:
            A list of log entries
        """
        return self.logs
    
    def clear(self) -> None:
        """Clear the captured logs."""
        self.logs = []
    
    def __enter__(self):
        """Start capturing logs when entering a context."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing logs when exiting a context."""
        self.stop()


def get_logger(
    name: str,
    level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = False,
    log_dir: str = "logs",
    structured: bool = False
) -> AgentLogger:
    """
    Get a logger for the agent framework.
    
    Args:
        name: The name of the logger
        level: The logging level
        console_output: Whether to output logs to the console
        file_output: Whether to output logs to a file
        log_dir: The directory to store log files
        structured: Whether to use structured logging (JSON format)
        
    Returns:
        An AgentLogger instance
    """
    return AgentLogger(
        name=name,
        level=level,
        console_output=console_output,
        file_output=file_output,
        log_dir=log_dir,
        structured=structured
    )

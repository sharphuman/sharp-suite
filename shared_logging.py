"""
Sharp Suite - Shared Logging Module
====================================
Provides consistent logging across all apps with:
- Console output (Railway logs)
- Supabase storage (Admin dashboard)
- Log levels: DEBUG, INFO, WARN, ERROR
"""
import os
import requests
from datetime import datetime
from functools import wraps
import traceback

# Supabase config (same as shared_config)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://qkjtprqgblnfftrotyks.supabase.co")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"

# Log levels
DEBUG = "DEBUG"
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"

# Whether to store logs in Supabase (can be disabled for performance)
STORE_IN_SUPABASE = True

# Current app name (set by each app)
_current_app = "unknown"

def set_app_name(app_name: str):
    """Set the current app name for logging context."""
    global _current_app
    _current_app = app_name

def _write_to_supabase(level: str, message: str, details: dict = None):
    """Write log entry to Supabase app_logs table."""
    if not STORE_IN_SUPABASE or not SUPABASE_SERVICE_KEY:
        return
    
    try:
        key = SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY
        requests.post(
            f"{SUPABASE_URL}/rest/v1/app_logs",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "app": _current_app,
                "level": level,
                "message": message[:1000],  # Limit message length
                "details": details,
                "created_at": datetime.utcnow().isoformat()
            },
            timeout=5
        )
    except:
        # Don't let logging failures break the app
        pass

def _format_log(level: str, message: str) -> str:
    """Format log message with timestamp and app name."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] [{_current_app}] [{level}] {message}"

def debug(message: str, details: dict = None):
    """Log debug message (console only, not stored)."""
    print(_format_log(DEBUG, message))

def info(message: str, details: dict = None, store: bool = True):
    """Log info message."""
    print(_format_log(INFO, message))
    if store:
        _write_to_supabase(INFO, message, details)

def warn(message: str, details: dict = None):
    """Log warning message."""
    print(_format_log(WARN, message))
    _write_to_supabase(WARN, message, details)

def error(message: str, details: dict = None, exc: Exception = None):
    """Log error message with optional exception traceback."""
    if exc:
        tb = traceback.format_exc()
        details = details or {}
        details["traceback"] = tb
        message = f"{message}: {str(exc)}"
    print(_format_log(ERROR, message))
    _write_to_supabase(ERROR, message, details)

def log_import_status(success: bool, module_name: str, error_msg: str = None):
    """Log module import status."""
    if success:
        info(f"Successfully imported {module_name}", store=False)
    else:
        warn(f"Failed to import {module_name}: {error_msg}", {
            "module": module_name,
            "cwd": os.getcwd(),
            "files": os.listdir(".")[:20]
        })

def log_api_call(endpoint: str, status_code: int, duration_ms: float = None):
    """Log API call result."""
    level = INFO if status_code == 200 else WARN if status_code < 500 else ERROR
    msg = f"API {endpoint} returned {status_code}"
    if duration_ms:
        msg += f" ({duration_ms:.0f}ms)"
    
    if level == INFO:
        info(msg, store=False)  # Don't store successful API calls
    elif level == WARN:
        warn(msg, {"endpoint": endpoint, "status": status_code})
    else:
        error(msg, {"endpoint": endpoint, "status": status_code})

def log_user_action(user_email: str, action: str, details: dict = None):
    """Log user action for analytics."""
    info(f"User {user_email}: {action}", {
        "user": user_email,
        "action": action,
        **(details or {})
    })

def log_exception(exc: Exception, context: str = ""):
    """Log exception with full traceback."""
    error(f"Exception in {context}" if context else "Exception", exc=exc)

# Decorator for logging function calls
def logged(func):
    """Decorator to log function entry/exit and exceptions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        debug(f"Entering {func_name}")
        try:
            result = func(*args, **kwargs)
            debug(f"Exiting {func_name}")
            return result
        except Exception as e:
            log_exception(e, func_name)
            raise
    return wrapper


# ============================================
# SQL to create the app_logs table in Supabase:
# ============================================
"""
CREATE TABLE IF NOT EXISTS app_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    app VARCHAR(50) NOT NULL,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_app_logs_app ON app_logs(app);
CREATE INDEX idx_app_logs_level ON app_logs(level);
CREATE INDEX idx_app_logs_created ON app_logs(created_at DESC);

-- Auto-delete old logs (keep 7 days)
CREATE OR REPLACE FUNCTION delete_old_logs()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM app_logs WHERE created_at < NOW() - INTERVAL '7 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cleanup_old_logs
AFTER INSERT ON app_logs
EXECUTE FUNCTION delete_old_logs();
"""

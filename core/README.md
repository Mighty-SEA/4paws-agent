# Core Modules

Core modules untuk 4Paws Agent - berisi konfigurasi, logging, dan path utilities yang di-extract dari `agent.py`.

## 📁 Structure

```
core/
├── __init__.py     - Module exports
├── config.py       - Configuration (Config class)
├── logger.py       - Logging setup (LogManagerHandler)
└── paths.py        - Path utilities (get_base_dir, get_writable_dir)
```

## 🔧 Usage

### Import Everything
```python
from core import Config, setup_logging, get_log_manager_handler
from core import get_base_dir, get_writable_dir
```

### Configuration
```python
from core import Config

# Access config
print(Config.BASE_DIR)
print(Config.WRITABLE_DIR)
print(Config.FRONTEND_PORT)
print(Config.BACKEND_PORT)
print(Config.MARIADB_PORT)
```

### Logging
```python
from core import setup_logging, get_log_manager_handler

# Setup logging
log_file = Config.WRITABLE_DIR / 'agent.log'
logger, handler = setup_logging(log_file)

# Use logger
logger.info("Hello from agent!")

# Connect to LogManager (for Web GUI)
from core import get_log_manager_handler
handler = get_log_manager_handler()
handler.set_log_manager(log_manager)
```

### Paths
```python
from core import get_base_dir, get_writable_dir

# Get paths
base = get_base_dir()        # Where executable/script is
writable = get_writable_dir()  # Where logs/data can be written

# Handles Program Files vs portable mode automatically!
```

## ✨ Benefits

1. **Reusable**: Other files can import these modules
2. **Maintainable**: Easy to find and edit configuration
3. **Clean**: agent.py is more focused on business logic
4. **Testable**: Each module can be tested independently

## 🔄 Backward Compatibility

All existing imports from `agent.py` still work:
```python
from agent import Config  # Still works! ✅
```

## 📝 Version

- **Created**: October 5, 2025
- **Phase**: 1 (Core extraction)
- **Status**: ✅ Production ready

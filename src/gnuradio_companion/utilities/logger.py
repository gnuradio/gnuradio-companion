import functools
import logging
import sys


# --- Logging customizations ---

# If we are going to add new levels, why not have some fun?
logging.NOTICE = 35     # Not an error, but should always show if using the default level (WARNING).
logging.VERBOSE = 8     # Debug is useful information, so verbose is just debug + more.
logging.ANNOY = 6       # Someone just wants to annoy you with all the messages it produces.
logging.CHAOS = 4       # Ok, it is just pure chaos at this point
logging.TRACE = 2       # You really want to see everything? REALLY?? Are you sure???

# Make sure the new levels are associated with names
logging.addLevelName(logging.NOTICE, "NOTICE")
logging.addLevelName(logging.VERBOSE, "VERBOSE")
logging.addLevelName(logging.ANNOY, "ANNOY")
logging.addLevelName(logging.CHAOS, "CHAOS")
logging.addLevelName(logging.TRACE, "TRACE")


# There are multiple ways to create custom logger levels. This creates a new 
# custom logger class and adds partial functions rather than defining and 
# injecting each log function into the module separately. This allows for 
# additional customization in the logger if it is needed later.
class CustomLogger(logging.getLoggerClass()):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The new wonderful logging functions. Isn't it great?
        self.notice = functools.partial(self.log, logging.NOTICE)
        self.verbose = functools.partial(self.log, logging.VERBOSE)
        self.annoy = functools.partial(self.log, logging.ANNOY)
        self.chaos = functools.partial(self.log, logging.CHAOS)
        self.trace = functools.partial(self.log, logging.TRACE)


# Magic to inject our custom logger so all instances use it.
logging.setLoggerClass(CustomLogger)

# Immediately create the root logger using the base package name. This can 
# be configured later, but the logging hierachy may not be setup properly 
# if it isn't created first. Anything requesting the root logger will get
# a reference to this instance.
root_module = __name__.split(".")[0]
root_logger = logging.getLogger(root_module)


# Can be called later to configure the logger once user configurations are loaded.
def configure_logger(level=logging.WARNING):
    root_logger.setLevel(level)
    
    # Avoid adding duplicate handlers if this function is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Try to use rich for pretty logging, otherwise fall back to standard logging
    try:
        from rich.logging import RichHandler
        from rich.traceback import install as install_rich_traceback
        
        # Install rich traceback handler to make exceptions pretty
        install_rich_traceback(show_locals=True)
        
        handler = RichHandler(
            rich_tracebacks=True, 
            show_time=True, 
            show_level=True, 
            show_path=False
        )
        formatter = logging.Formatter("%(message)s")

    except ImportError:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="[%X]"
        )
        root_logger.debug("Using standard logging handler. Install 'rich' to enable extra formatting.")

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

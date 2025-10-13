import logging

# Immediately inject our custom logger. This also creates the root instance.
from .utilities import logger as custom_logging

# Just a sanity check, but it also stops unused import warnings.
root_logger = logging.getLogger(__name__)
assert(isinstance(root_logger, custom_logging.CustomLogger))

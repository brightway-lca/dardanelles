__all__ = ["dardanelles_app"]

__version__ = (0, 1)

from flask import Flask

dardanelles_app = Flask("dardanelles")

# Default limit for file uploads is 250 MB
dardanelles_app.config["MAX_CONTENT_LENGTH"] = 250 * 1024 * 1024

from . import app

__all__ = ["dardanelles_app"]

__version__ = (0, 1)

from pathlib import Path

from flask import Flask

template_dir = Path(__file__).parent.resolve() / "templates"
dardanelles_app = Flask("dardanelles", template_folder=template_dir)

# Default limit for file uploads is 128 MB
dardanelles_app.config["MAX_CONTENT_LENGTH"] = 128 * 1024 * 1024

from . import app

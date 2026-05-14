# =============================================================
# AION Web Framework — Package Init
# =============================================================
# Makes the web module importable from anywhere like:
#   from web import load_web_module

from web.web_module import load
from web.server import AIONServer
from web.router import Router
from web.request import AIONRequest
from web.response import (
    AIONResponse, text_response,
    json_response, html_response, error_response
)


def load_web_module() -> dict:
    """Load all web functions into the AION environment."""
    return load()
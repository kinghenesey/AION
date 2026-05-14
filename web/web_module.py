# =============================================================
# AION Web Framework — Web Module
# =============================================================
# This is what gets loaded when you write "use web" in AION.
# It exposes all web functions to your AION programs.
#
# Usage in AION:
#   use web
#   web_route("/", "Hello World!")
#   web_route("/about", "About page")
#   web_start(8000)

from web.server import AIONServer
from web.request import AIONRequest
from web.response import (
    text_response, json_response,
    html_response, error_response
)


# Global server instance
_server = None


def load() -> dict:
    """
    Returns all web functions to be loaded
    into the AION environment when 'use web' is called.
    """
    return {
        # Server management
        "web_app":      _web_app,
        "web_start":    _web_start,

        # Routing
        "web_route":    _web_route,
        "web_get":      _web_get,
        "web_post":     _web_post,

        # Response helpers
        "web_text":     lambda content: text_response(content).body,
        "web_json":     lambda data:    json_response(data).body,
        "web_html":     lambda content: html_response(content).body,

        # Request helpers (used inside handlers)
        "web_param":    _web_param,
    }


# ----------------------------------------------------------
# Server management
# ----------------------------------------------------------

def _web_app(name: str = "AION Web App"):
    """Create and configure the web server."""
    global _server
    _server = AIONServer(name=str(name))
    return name


def _web_start(port: int = 8000):
    """Start the web server."""
    global _server

    if _server is None:
        _server = AIONServer("AION Web App")

    _server.start(port=int(port))


# ----------------------------------------------------------
# Routing
# ----------------------------------------------------------

def _web_route(path: str, response,
               methods: list = None):
    """
    Register a route with a static or dynamic response.

    Usage in AION:
        web_route("/", "Welcome!")
        web_route("/hello", "Hello World!")
    """
    global _server

    if _server is None:
        _server = AIONServer("AION Web App")

    if methods is None:
        methods = ["GET"]

    # If response is a string, wrap in a handler
    if isinstance(response, str):
        content = response
        def handler(request: AIONRequest):
            return text_response(content)
    elif isinstance(response, dict):
        data = response
        def handler(request: AIONRequest):
            return json_response(data)
    elif callable(response):
        handler = response
    else:
        content = str(response)
        def handler(request: AIONRequest):
            return text_response(content)

    _server.router.add(path, handler, methods=methods)
    return path


def _web_get(path: str, response):
    """Register a GET route."""
    return _web_route(path, response, methods=["GET"])


def _web_post(path: str, response):
    """Register a POST route."""
    return _web_route(path, response, methods=["POST"])


def _web_param(name: str, default: str = "") -> str:
    """
    Get a URL parameter from the current request.
    Used inside route handlers.
    """
    return default
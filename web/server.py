# =============================================================
# AION Web Framework — Server
# =============================================================
# Wraps Flask to create a real HTTP server.
# The Router handles all URL dispatching.
# Flask handles the actual HTTP layer.
#
# Usage:
#   server = AIONServer(router)
#   server.start(port=8000)

import os
import sys
from web.router import Router
from web.request import from_flask_request
from web.response import AIONResponse


class AIONServer:
    """
    A real HTTP server powered by Flask.

    Usage:
        server = AIONServer()
        server.router.add("/", handler)
        server.start(8000)
    """

    def __init__(self, name: str = "AION App"):
        self.name   = name
        self.router = Router()
        self._app   = None

    def start(self, port: int = 8000, debug: bool = False):
        """
        Start the HTTP server on the given port.
        Blocks until the server is stopped (Ctrl+C).
        """
        self._setup_flask()

        from config import Color
        print()
        print(f"{Color.CYAN}{Color.BOLD}  AION Web Server{Color.RESET}")
        print(f"  {Color.DIM}{'─' * 40}{Color.RESET}")
        print(f"  {Color.GREEN}✓ Server running at "
              f"http://localhost:{port}{Color.RESET}")
        print(f"  {Color.DIM}Press Ctrl+C to stop{Color.RESET}")
        print()

        # Show registered routes
        for route in self.router.get_routes():
            methods = ", ".join(route.methods)
            print(f"  {Color.DIM}→ {methods:<6} "
                  f"{route.path}{Color.RESET}")
        print()

        # Suppress Flask startup messages
        import logging
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        self._app.run(
            host="0.0.0.0",
            port=int(port),
            debug=debug,
            use_reloader=False
        )

    def _setup_flask(self):
        """Configure Flask to use our router."""
        from flask import Flask, request as flask_request

        self._app = Flask(self.name)

        # Catch-all route — send everything to our router
        @self._app.route("/", defaults={"path": ""})
        @self._app.route("/<path:path>", methods=[
            "GET", "POST", "PUT", "DELETE", "PATCH"
        ])
        def handle_all(path):
            from flask import Response as FlaskResponse

            # Convert Flask request to AION request
            aion_request  = from_flask_request(flask_request)
            aion_response = self.router.handle(aion_request)

            return FlaskResponse(
                response=aion_response.body,
                status=aion_response.status,
                headers=aion_response.headers,
                content_type=aion_response.content_type,
            )

    def __repr__(self):
        return f"AIONServer({self.name})"
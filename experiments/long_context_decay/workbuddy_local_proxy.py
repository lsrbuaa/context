#!/usr/bin/env python3
"""
WorkBuddy Local Proxy Server

A local HTTP server that receives evaluation prompts and processes them
by spawning a fresh WorkBuddy CLI session for each request.
Each request gets a completely fresh context window.

Usage:
    python workbuddy_local_proxy.py --port 5123

Then configure run_config.json to use:
    "provider": {
        "type": "http",
        "http_url": "http://127.0.0.1:5123/eval",
        "http_headers": {}
    }
"""

import argparse
import json
import os
import signal
import socket
import socketserver
import sys
import threading
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Timeout for model response (seconds)
MODEL_TIMEOUT = 120

# Port for the local proxy server
PORT = 5123


class ProxyHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the local proxy server."""

    def log_message(self, format, *args):
        """Suppress default logging; use our own."""
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}", file=sys.stderr)

    def do_POST(self):
        """Handle POST requests to /eval endpoint."""
        if self.path != "/eval":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        system_prompt = payload.get("system", "")
        user_prompt = payload.get("prompt", "")
        metadata = payload.get("metadata", {})

        print(f"  -> Case: {metadata.get('case_id', 'unknown')}, "
              f"Tier: {metadata.get('tier', '?')}, "
              f"Category: {metadata.get('category', '?')}")

        # Call the model with a fresh context
        # NOTE: This is a placeholder. The actual implementation depends on
        # how to spawn a fresh WorkBuddy session from the command line.
        #
        # Option A: Use WorkBuddy CLI (if available)
        # Option B: Use an API endpoint with a fresh session each time
        # Option C: Use a custom script that invokes the model
        response_text, latency_ms, input_tokens, output_tokens = \
            call_model_fresh(system_prompt, user_prompt, metadata)

        # Return the response
        result = {
            "text": response_text,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "metadata": metadata,
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "port": PORT}).encode())
        else:
            self.send_response(404)
            self.end_headers()


def call_model_fresh(system_prompt: str, user_prompt: str, metadata: dict) -> tuple:
    """
    Call the model with a FRESH context window.

    This is the key function that must be implemented correctly.
    Each call must use a completely fresh context window.

    Current approach: Use the WorkBuddy API with stateless requests.
    Each HTTP request without a conversation_id gets a fresh context.

    Returns:
        (response_text, latency_ms, input_tokens, output_tokens)
    """
    # TODO: Implement this using the correct API endpoint and authentication
    # For now, return a placeholder response
    
    print("WARNING: call_model_fresh is not yet implemented correctly.")
    print("Please configure the correct API endpoint and authentication.")
    
    # Placeholder response
    response_text = json.dumps({"answer": "PLACEHOLDER - not implemented yet"})
    latency_ms = 0
    input_tokens = 0
    output_tokens = 0
    
    return response_text, latency_ms, input_tokens, output_tokens


def find_free_port():
    """Find a free port to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description="WorkBuddy Local Proxy Server")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), ProxyHandler)
    print(f"WorkBuddy Local Proxy listening on http://{args.host}:{args.port}")
    print(f"  Endpoint: http://{args.host}:{args.port}/eval")
    print(f"  Health check: http://{args.host}:{args.port}/health")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()

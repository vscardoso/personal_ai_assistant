#!/usr/bin/env python3
"""
Simple HTTP server for serving the landing page.
Usage: python server.py [port]
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def serve_landing_page(port=8080):
    """Serve the landing page on the specified port."""

    # Change to the frontend directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)

    # Create handler for serving files
    Handler = http.server.SimpleHTTPRequestHandler

    # Add proper MIME types
    Handler.extensions_map.update({
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
    })

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Landing page servidor iniciado!")
            print(f"Acesse: http://localhost:{port}")
            print(f"Servindo arquivos de: {frontend_dir}")
            print(f"API Backend: http://localhost:8000")
            print(f"Pressione Ctrl+C para parar")
            print("-" * 50)

            httpd.serve_forever()

    except KeyboardInterrupt:
        print(f"\nServidor parado.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Porta {port} ja esta em uso.")
            print(f"Tente: python server.py {port + 1}")
        else:
            print(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Get port from command line argument or use default
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Porta deve ser um numero inteiro")
            print("Uso: python server.py [porta]")
            sys.exit(1)

    serve_landing_page(port)
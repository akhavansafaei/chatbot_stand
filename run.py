#!/usr/bin/env python3
"""
Startup script for Chatbot Stand
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import and run server
from websocket_server import ChatbotServer

if __name__ == "__main__":
    config_path = "config.yaml"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    print("=" * 60)
    print("Chatbot Stand - Real-time AI Assistant")
    print("=" * 60)
    print(f"Loading configuration from: {config_path}")

    try:
        server = ChatbotServer(config_path)
        print("\nServer starting...")
        print("Open your browser and navigate to: http://localhost:8000")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        server.run()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

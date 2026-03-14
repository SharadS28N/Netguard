"""
Netguard WSGI Entry Point
---
Selects a production-grade server based on the OS.
- Windows: Waitress
- Linux/macOS: Gunicorn
"""

import os
import platform
import subprocess
import sys

from app import create_app, get_config

# Create the Flask app instance from the factory
app = create_app()
config = get_config()

# Get host and port from config, with fallbacks
host = getattr(config, "HOST", "0.0.0.0")
port = getattr(config, "PORT", 5001)


def main():
    """
    Production entry point.
    Selects and runs a production server based on the operating system.
    """
    system = platform.system()
    is_debug = getattr(config, "DEBUG", False)

    print(f"Platform: {system} | Debug: {is_debug}")

    if system == "Windows":
        print(f"Starting Waitress server on http://{host}:{port}")
        try:
            from waitress import serve

            serve(app, host=host, port=port)
        except ImportError:
            print(
                "ERROR: waitress is not installed. Run 'pip install waitress'.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        # Assume Linux or macOS, use Gunicorn
        workers = (os.cpu_count() or 1) * 2 + 1
        print(
            f"Starting Gunicorn server on http://{host}:{port} with {workers} workers"
        )

        try:
            # Verify gunicorn is available
            subprocess.run(
                ["gunicorn", "--version"], check=True, capture_output=True, text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "ERROR: gunicorn is not installed. Run 'pip install gunicorn'.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Construct Gunicorn command
        args = [
            "gunicorn",
            "--bind",
            f"{host}:{port}",
            "--workers",
            str(workers),
            "--log-level",
            "info",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
            "wsgi:app",
        ]
        if is_debug:
            args.append("--reload")

        # Execute Gunicorn
        try:
            subprocess.run(args, check=True)
        except KeyboardInterrupt:
            print("Gunicorn server stopped.")
        except Exception as e:
            print(f"Failed to start Gunicorn: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

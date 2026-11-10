"""Start the development server:  python backend/run.py"""
import sys
from pathlib import Path

# Make `scheduling` (repo root) importable from the backend.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

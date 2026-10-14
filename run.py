"""Точка входа: python run.py (браузер откроется сам).

Библиотеки лежат в папке lib/ рядом — никакой установки не требуется.
"""

import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT))

from ritmika import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000)

#!/usr/bin/env python3
"""CLI entrypoint for the Telegram bot.

Implementation lives in `src/chatbot/telegram_bot.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.chatbot.telegram_bot import main


if __name__ == "__main__":
    main()


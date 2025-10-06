#!/usr/bin/env python3
"""Test script to check if the Telegram API imports correctly."""

try:
    print("Testing imports...")
    import app.telegram.main
    print("SUCCESS: Import successful!")
except Exception as e:
    print(f"FAILED: Import failed: {e}")
    import traceback
    traceback.print_exc()

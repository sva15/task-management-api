#!/usr/bin/env python3
"""Simple test to diagnose import issues."""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.main import app, tasks_db
    print("✓ Import successful")
    print(f"App title: {app.title}")
    print(f"Tasks DB type: {type(tasks_db)}")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")

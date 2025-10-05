# Cursor Rules for Wanderer MIDI Project

## General Preferences

- Do not create test scripts unless explicitly requested
- Always activate the virtual environment before running shell commands
- Do not comment about the quality of my questions
- We are making a prototype and iterating quickly, keeping things lean

## Project Context

- This is a MIDI processing application with real-time audio
- Main entrypoint is main.py
- Services run in background threads to avoid blocking
- UI uses webview for real-time MIDI visualization

## Code Style

- Use type hints where appropriate
- Keep services loosely coupled
- Do not add comments when code is obvious
- We control everything here, no need for a lot of defensive try/catch if/else code

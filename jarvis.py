"""JARVIS: a small, voice-controlled assistant with native macOS speech output."""

from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import sys
import webbrowser
from urllib.parse import quote_plus

LANGUAGE = os.getenv("JARVIS_LANGUAGE", "en-IN")

EXIT_COMMANDS = {
    "bye",
    "goodbye",
    "good bye",
    "okay bye",
    "ok bye",
    "exit",
    "quit",
    "stop",
    "stop listening",
}
HELP_COMMANDS = {"help", "commands", "what can you do"}
TIME_COMMANDS = {"time", "what time is it", "whats the time", "tell me the time"}
DATE_COMMANDS = {"date", "what is the date", "whats the date", "todays date", "what day is it"}
OPEN_GOOGLE_COMMANDS = {"open google", "launch google"}
OPEN_YOUTUBE_COMMANDS = {"open youtube", "launch youtube"}


def normalize_command(query: str) -> str:
    """Normalize a command for matching without relying on substring tests."""
    normalized = re.sub(r"[^\w\s]", "", query.casefold())
    return " ".join(normalized.split())


def parse_command(query: str) -> tuple[str, str]:
    """Return (action, argument) for a spoken command; this function is testable."""
    raw = (query or "").strip()
    if not raw:
        return ("empty", "")

    normalized = normalize_command(raw)
    if normalized.startswith("jarvis "):
        normalized = normalized[len("jarvis ") :].strip()
        raw = re.sub(r"^jarvis[\s,]+", "", raw, flags=re.IGNORECASE).strip()

    if normalized in EXIT_COMMANDS:
        return ("exit", "")
    if normalized in HELP_COMMANDS:
        return ("help", "")
    if normalized in TIME_COMMANDS:
        return ("time", "")
    if normalized in DATE_COMMANDS:
        return ("date", "")
    if normalized in OPEN_GOOGLE_COMMANDS:
        return ("open_url", "https://www.google.com")
    if normalized in OPEN_YOUTUBE_COMMANDS:
        return ("open_url", "https://www.youtube.com")

    match = re.match(r"^(?:search\s+)?wikipedia(?:\s+for)?\s+(.+)$", raw, flags=re.IGNORECASE)
    if match:
        topic = match.group(1).strip()
        return ("wikipedia", topic) if topic else ("help", "")

    match = re.match(r"^wiki\s+(.+)$", raw, flags=re.IGNORECASE)
    if match:
        return ("wikipedia", match.group(1).strip())

    match = re.match(r"^(?:search\s+for|google)\s+(.+)$", raw, flags=re.IGNORECASE)
    if match:
        search_term = match.group(1).strip()
        return ("web_search", search_term) if search_term else ("help", "")

    return ("unknown", raw)


def speak(message: str) -> None:
    """Speak through macOS's built-in say command; remain usable in a terminal."""
    print(f"JARVIS: {message}")
    if sys.platform != "darwin":
        return
    try:
        subprocess.run(
            ["say", message],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        print("Voice output is unavailable; continuing in text mode.")


def listen_for_command(recognizer, speech_recognition) -> str | None:
    """Record one utterance and transcribe it using Google's online recognizer."""
    try:
        with speech_recognition.Microphone() as source:
            print("\nListening... (speak a command)")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
    except speech_recognition.WaitTimeoutError:
        print("No speech detected. Try again.")
        return None

    try:
        command = recognizer.recognize_google(audio, language=LANGUAGE)
        print(f"You: {command}")
        return command
    except speech_recognition.UnknownValueError:
        speak("I couldn't understand that. Please try again.")
    except speech_recognition.RequestError:
        speak("Speech recognition is unavailable. Check your internet connection.")
    return None


def execute_command(
    query: str,
    speaker=speak,
    open_url=webbrowser.open,
) -> bool:
    """Execute a recognized command. Return False when the assistant should exit."""
    action, argument = parse_command(query)

    if action == "empty":
        return True
    if action == "exit":
        speaker("Goodbye.")
        return False
    if action == "help":
        speaker(
            "You can ask me to open Google or YouTube, tell the time or date, "
            "search the web, or summarize a Wikipedia topic. Say goodbye to exit."
        )
    elif action == "time":
        speaker(f"It is {dt.datetime.now().astimezone().strftime('%I:%M %p')}.")
    elif action == "date":
        speaker(f"Today is {dt.date.today().strftime('%A, %B %d, %Y')}.")
    elif action == "open_url":
        open_url(argument)
        speaker(f"Opening {argument.removeprefix('https://www.')}.")
    elif action == "web_search":
        url = f"https://www.google.com/search?q={quote_plus(argument)}"
        open_url(url)
        speaker(f"Searching the web for {argument}.")
    elif action == "wikipedia":
        try:
            import wikipedia

            summary = wikipedia.summary(argument, sentences=2, auto_suggest=True)
            speaker(f"According to Wikipedia: {summary}")
        except Exception:
            # Covers disambiguation, missing pages, and temporary network/API failures.
            speaker(
                f"I couldn't get a summary for {argument}. "
                "Try a more specific topic or check your internet connection."
            )
    else:
        speaker("I don't know that command yet. Say help to hear supported commands.")

    return True


def create_recognizer():
    """Import optional audio dependencies only when starting the live assistant."""
    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise RuntimeError(
            "SpeechRecognition is not installed. Run: python -m pip install -r requirements.txt"
        ) from exc

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Calibrating microphone for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
    except (AttributeError, OSError) as exc:
        raise RuntimeError(
            "Could not access a microphone. Install the audio dependencies and allow "
            "microphone access for Terminal or your IDE in macOS System Settings."
        ) from exc
    return sr, recognizer


def main() -> int:
    """Start the interactive voice-assistant loop."""
    try:
        speech_recognition, recognizer = create_recognizer()
    except RuntimeError as exc:
        print(f"JARVIS setup error: {exc}", file=sys.stderr)
        return 1

    speak("JARVIS is ready. Say help to hear what I can do.")
    try:
        while True:
            query = listen_for_command(recognizer, speech_recognition)
            if query is not None and not execute_command(query):
                break
    except KeyboardInterrupt:
        speak("Goodbye.")
    except OSError as exc:
        print(f"Audio device error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

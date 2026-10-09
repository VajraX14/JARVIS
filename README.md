# JARVIS — macOS Voice Assistant

A small Python voice assistant, updated to run on macOS (including Apple Silicon / M1). It keeps the original project's purpose—hands-free commands—while replacing the Windows-only SAPI5 voice engine and fixing command matching.

## What it can do

Say one of these commands after JARVIS says it is listening:

- **"Open Google"** or **"Open YouTube"** — open the site in your default browser.
- **"Search for [topic]"** or **"Google [topic]"** — open a Google search.
- **"Wikipedia for [topic]"** or **"Wiki [topic]"** — read a short Wikipedia summary aloud.
- **"What time is it?"** or **"What is the date?"**
- **"Help"** — hear the supported commands.
- **"Goodbye"**, **"Exit"**, or **"Stop listening"** — quit.

There is no always-on wake-word detector: the assistant listens for one utterance at a time and then processes it.

## Requirements

- macOS on Apple Silicon or Intel
- Python 3.10 or later
- Homebrew (to install the microphone's PortAudio dependency)
- A microphone and internet access for online speech recognition and Wikipedia summaries

## Setup on a Mac M1

Open Terminal and run:

```bash
# 1. Install PortAudio (needed by PyAudio for microphone input)
brew install portaudio

# 2. Get the project
git clone https://github.com/VajraX14/JARVIS.git
cd JARVIS

# 3. Use the modernization branch
git switch modernize/macos-apple-silicon

# 4. Create and activate an isolated Python environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install Python dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 6. Start JARVIS
python jarvis.py
```

If the branch has not yet been merged into `master`, the `git switch` command above is required. If you have already cloned the repository, run `git fetch origin` before switching.

### Microphone permission

On the first run, macOS may ask for microphone access. If not, open **System Settings → Privacy & Security → Microphone** and enable access for the app you use to run JARVIS (for example, Terminal or your IDE). Quit and reopen that app after changing permission.

### If PyAudio fails to install

Confirm that Homebrew's `portaudio` package installed correctly, then reactivate the virtual environment and retry:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install "SpeechRecognition[audio]"
```

Use the same CPU architecture for Python and Homebrew (native Apple Silicon installations are normally under `/opt/homebrew`). Avoid mixing an Intel/Rosetta Python with ARM-native dependencies.

## Run the tests

The command parser and exit behavior can be tested without a microphone or network connection:

```bash
python -m unittest discover -s tests -v
```

## Privacy and limitations

- Speech-to-text uses SpeechRecognition's Google web recognizer; recorded speech is sent to the service for transcription. Do not speak passwords, recovery codes, financial details, or other sensitive information.
- Wikipedia summaries also require an internet connection.
- Voice output uses macOS's built-in `say` command; JARVIS does not install a separate speech engine.
- This is a rule-based assistant, not an LLM-powered agent. It only executes explicitly supported commands.
- Commands open websites in your default browser. JARVIS does not run arbitrary terminal commands.

## Troubleshooting

- **No microphone / `Microphone` error:** install the dependencies and grant microphone permission in macOS settings.
- **Speech recognition fails:** check internet connectivity; try speaking clearly after the listening prompt.
- **JARVIS does not understand a phrase:** use one of the example commands above.
- **No audible response:** check the Mac's output device and volume. Responses are also printed in the terminal.

## Project files

- `jarvis.py` — assistant, speech input/output, and command routing
- `requirements.txt` — Python dependencies
- `tests/` — offline unit tests for command routing


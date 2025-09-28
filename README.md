# Wanderer

Transforms incoming notes to their random harmonics.

## Dependencies

You may need to install XCode CLI tools.

```bash
xcode-select --install
sudo xcodebuild -license accept   # or open Xcode once and accept UI prompt
clang++ --version                 # sanity check
```

Install Python dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
```

## Run

Execute the host file. This will expose Python MIDI ports you can map to and from in your DAW.

```bash
python host.py
```

## Audio Sample

Here is a sample of the audio output. The input is just one note repeated.

<audio controls>
  <source src="sample.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

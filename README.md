# srt-translator

`srt-translator` is a tool for translating SRT subtitle files.

## Installation

```bash
python -m venv venv
source venv/bin/activate

pip install git+https://github.com/unclefomotw/srt-translator.git
```

## How to use

```bash
$ srt-translate -h
usage: srt-translate [-h] -i INPUT -o OUTPUT -s SOURCE -t TARGET [-m MODEL] [--knowledge [KNOWLEDGE ...]]

Translate SRT subtitles using LLM.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input SRT file
  -o OUTPUT, --output OUTPUT
                        Output file for translated subtitles
  -s SOURCE, --source SOURCE
                        Source language
  -t TARGET, --target TARGET
                        Target language
  -m MODEL, --model MODEL
                        Model string in the format of "provider:model"
  --knowledge [KNOWLEDGE ...]
                        Additional domain knowledge text files

```

An example
```bash
srt-translate -i /tmp/captions.srt -o /tmp/translation.srt -s Chinese -t English -m openai:gpt-4o-mini
```
from pathlib import Path
from typing import Optional

import aisuite as ai
import srt
from dotenv import load_dotenv

from srt_translator.translator.llm_translator import LLMTranslator

PathLike = str | Path

N_CONTEXT_BEFORE = 5
N_CONTEXT_AFTER = 3
N_BATCH = 3


def translate(srt_file: PathLike,
              source_lang: str,
              target_lang: str,
              model: str = "openai:gpt-4o-mini",
              domain_knowledge_str: str = "",
              domain_knowledge_files: Optional[list[PathLike]] = None) -> str:

    with open(srt_file) as f:
        subtitles = list(srt.parse(f.read()))

    translator = LLMTranslator(ai.Client(), model)

    domain_context = domain_knowledge_str + "\n"
    if domain_knowledge_files:
        for file in domain_knowledge_files:
            with open(file) as f:
                domain_context += f.read() + "\n"

    translated_subtitles = []

    for i in range(0, len(subtitles), N_BATCH):
        subtitle_batch = subtitles[i:i + N_BATCH]

        context_subtitles = subtitles[max(0, i - N_CONTEXT_BEFORE) : i + N_BATCH + N_CONTEXT_AFTER]
        context = "\n".join([s.content for s in context_subtitles])

        batch_translation = translator.translate(source_lang, target_lang,
                                                 subtitle_batch, context, domain_context)
        translated_subtitles.extend(batch_translation)

    return srt.compose(translated_subtitles)


if __name__ == "__main__":
    load_dotenv()
    r = translate("/tmp/captions.srt", "Chinese", "English")
    print(r)
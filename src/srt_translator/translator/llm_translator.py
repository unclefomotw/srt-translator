import re

import aisuite as ai
import srt

from srt_translator.translator.base import Translator

SYSTEM_PROMPT_TEMPLATE = """You are an experienced translator. Both {source_lang} and {target_lang}
are your native languages. Your job is to translate subtitles from {source_lang} to {target_lang}.

The characteristics of these subtitles are as follows:
* Subtitles are made of lines of text, each of which has an implicit timestamp.
* Therefore translation should be done line by line.
* And you should not change the order of the lines.

Line-by-line translation is challenging because you need to maintain the context of the conversation.
Therefore context and domain knowledge are provided to you.
* Make sure to take advantage of the context and domain knowledge so you can make better translations.
* Make sure to keep the translation natural and fluent.
"""

USER_PROMPT_TEMPLATE = """Your job is to translate subtitles from {source_lang} to {target_lang}.
You will be given a context and domain knowledge to help you with the translation.

The following is the context, which surrounds the subtitles you need to translate:
<CONTEXT>
{subtitle_context}
</CONTEXT>

The following is the domain knowledge, which you can use to make better translations:
<DOMAIN_KNOWLEDGE>
{domain_context}
</DOMAIN_KNOWLEDGE>

The subtitles you need to translate are enclosed in <TRANSLATE_THIS> and </TRANSLATE_THIS> tags.
Please translate thems line by line, and enclose the output between <TRANSLATION> and </TRANSLATION>.

Here is an example of input and output:
The input:
<TRANSLATE_THIS>
你好嗎？
我很好，謝謝
</TRANSLATE_THIS>

You should output:
<TRANSLATION>
How are you?
I'm fine, thank you
</TRANSLATION>

Note that the input and output should have the same number of lines.

Now, please translate the subtitles:
<TRANSLATE_THIS>
{subtitles}
</TRANSLATE_THIS>
"""

OUTPUT_PATTERN = re.compile(r'<TRANSLATION>(.*?)</TRANSLATION>', re.DOTALL)


class LLMTranslator(Translator):
    def __init__(self, client: ai.Client, model: str):
        self.client = client
        self.model_name = model

    def translate(self, source_lang: str,
                  target_lang: str,
                  subtitles: list[srt.Subtitle],
                  subtitle_context: str,
                  domain_context: str) -> list[srt.Subtitle]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(source_lang=source_lang,
                                                                        target_lang=target_lang)},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                source_lang=source_lang,
                target_lang=target_lang,
                subtitle_context=subtitle_context,
                domain_context=domain_context,
                subtitles="\n".join([subtitle.content for subtitle in subtitles])
                )}
        ]

        response = self.client.chat.completions.create(model=self.model_name, messages=messages)
        response_content = response.choices[0].message.content
        match = OUTPUT_PATTERN.search(response_content)
        if match:
            translations = [s.strip() for s in match.group(1).split("\n") if s.strip()]
        else:
            raise ValueError(f"Translation error: {response_content}")

        if len(subtitles) != len(translations):
            raise ValueError("Number of subtitles and translations do not match: " + match.group(1))

        return self.make_new_subtitles(subtitles, translations)

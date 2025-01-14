import aisuite as ai
import srt
from dotenv import load_dotenv

from srt_translator.translator.llm_translator import LLMTranslator


def test():
    load_dotenv()
    with open("/tmp/captions.srt") as f:
        subtitles = list(srt.parse(f.read()))
        context = "\n".join([s.content for s in subtitles[:10]])
        client = ai.Client()
        translator = LLMTranslator(client, "openai:gpt-4o-mini")
        print(subtitles[5:7])
        r = translator.translate("Chinses", "English", subtitles[5:7], context, "")
        print(r)


if __name__ == "__main__":
    test()
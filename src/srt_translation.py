import argparse
from typing import List, Union, TypeVar, Iterator, Tuple

from openai import OpenAI

T = TypeVar("T")

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-i", "--input_file", type=str, required=True,
                        help="Input SRT file")
arg_parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Output SRT file")

class SRTLine:
    order: int
    time_str: str
    content: str

    def __init__(self, order: Union[int, str], time_str: str, content: str):
        self.order = int(order)
        self.time_str = time_str
        self.content = content

    def __repr__(self):
        return f'"{self.order}\n{self.time_str}\n{self.content}"'

    def __str__(self):
        return f"{self.order}\n{self.time_str}\n{self.content}\n\n"

    @staticmethod
    def verify_srt_line(line_no, line) -> str:
        line_kind_no = line_no % 4
        if line_kind_no == 1:
            try:
                int(line)
            except ValueError:
                raise ValueError(f"Expect an SRT No. in Line {line_no}: {line}")
            return "order"
        elif line_kind_no == 2:
            if "-->" not in line:
                raise ValueError(f"Expect time string in Line {line_no}: {line}")
            return "time_str"
        elif line_kind_no == 3:
            if line == "":
                raise ValueError(f"Expect content in Line {line_no}: {line}")
            return "content"
        else:
            if line != "":
                raise ValueError(f"Expect an empty line in Line {line_no}: {line}")
            return "_eol"


OPENAI_SYSTEM_PROMPT = """You are an agent that translates Traditional Chinese into English.
I give you one line of text to translate, along with lines surrounding it as the context.
Translate the line I want you to translate based on the given context, so that the grammar or the tone can be consistent.
Output only the translation of the line."""

OPENAI_MSG_TEMPLATE = """Context:
```
{context}
```

Line to translate:
```
{line_to_translate}
```
"""

# OPENAI_MODEL = "gpt-4-turbo-preview"
OPENAI_MODEL = "gpt-3.5-turbo"

client = OpenAI()


def parse_srt_file(filename) -> Iterator[SRTLine]:
    line_no = 0
    _srt_tmp = dict()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            line_no += 1
            line_kind = SRTLine.verify_srt_line(line_no, line)
            if line_kind == "_eol":
                yield SRTLine(_srt_tmp["order"], _srt_tmp["time_str"], _srt_tmp["content"])
                _srt_tmp = dict()
            else:
                _srt_tmp[line_kind] = line


    if line_kind != "_eol":
        raise ValueError("The SRT file is not completed")


def _get_batch_generator(input_list: list[T], batch_size=10):
    for i in range(0, len(input_list), batch_size):
        yield input_list[i : i + batch_size]


def translate(line_to_translate: str, context: str) -> str:
    print(line_to_translate)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": OPENAI_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": OPENAI_MSG_TEMPLATE.format(line_to_translate=line_to_translate,
                                                      context=context)
            },
        ],
        temperature=0,
    )
    output = response.choices[0].message.content

    return output


def main(args):
    input_srt_file = args.input_file
    output_srt_file = args.output_file

    srt_lines: List[SRTLine] = list(parse_srt_file(input_srt_file))
    translated_srt_lines: List[SRTLine] = []

    for i in range(len(srt_lines)):
        original_srt_line = srt_lines[i]

        line_to_translate = original_srt_line.content
        context = "\n".join([
            l.content
            for l in srt_lines[max(0, i-2): i+3]
        ])

        line_translation = translate(line_to_translate, context)

        translated_srt_lines.append(
            SRTLine(
                order=original_srt_line.order,
                time_str=original_srt_line.time_str,
                content=line_translation
            )
        )

    with open(output_srt_file, "w") as f_out:
        for translated_srt_line in translated_srt_lines:
            f_out.write(str(translated_srt_line))


if __name__ == '__main__':
    parsed_args = arg_parser.parse_args()
    main(parsed_args)

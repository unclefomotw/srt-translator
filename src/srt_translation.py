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


OPENAI_SYSTEM_PROMPT = """
You are an agent that translates Traditional Chinese into English.
I give you one paragraph of lines in the same topic and context.
You translate each line and output in a line itself.  Use line breaks to separate each translated line.
In other words, if I give you 10 lines, you output 10 lines.
"""
# OPENAI_MODEL = "gpt-4-turbo-preview"
OPENAI_MODEL = "gpt-3.5-turbo"

BATCH_SIZE = 20

client = OpenAI()


def parse_srt_file(filename) -> List[SRTLine]:
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


def translate(line_strings: list):
    print(line_strings)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": OPENAI_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": "\n".join(line_strings)
            },
        ],
        temperature=0,
    )
    output = response.choices[0].message.content
    output_lines = output.split("\n")
    if len(output_lines) != len(line_strings):
        raise ValueError(f"translation amount is different: {output}")

    return output_lines


def main(args):
    input_srt_file = args.input_file
    output_srt_file = args.output_file

    srt_lines = list(parse_srt_file(input_srt_file))
    translated_srt_lines: List[SRTLine] = []

    for srt_line_batch in _get_batch_generator(srt_lines, batch_size=BATCH_SIZE):
        line_translations = translate([l.content for l in srt_line_batch])

        zipped: Iterator[Tuple[SRTLine, str]] = zip(srt_line_batch, line_translations)
        for _s, _t in zipped:
            translated_srt_lines.append(
                SRTLine(
                    order=_s.order,
                    time_str=_s.time_str,
                    content=_t
                )
            )

    with open(output_srt_file, "w") as f_out:
        for translated_srt_line in translated_srt_lines:
            f_out.write(str(translated_srt_line))


if __name__ == '__main__':
    parsed_args = arg_parser.parse_args()
    main(parsed_args)

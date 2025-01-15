import argparse

from dotenv import load_dotenv

from srt_translator.translate import translate


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Translate SRT subtitles using LLM.")
    parser.add_argument('-i', '--input', required=True, help='Input SRT file')
    parser.add_argument('-o', '--output', required=True, help='Output file for translated subtitles')
    parser.add_argument('-s', '--source', required=True, help='Source language')
    parser.add_argument('-t', '--target', required=True, help='Target language')
    parser.add_argument('-m', '--model', default="openai:gpt-4o-mini",
                        help='Model string in the format of "provider:model"')
    parser.add_argument('--knowledge', nargs='*', help='Additional domain knowledge text files')

    args = parser.parse_args()

    domain_knowledge = ""
    if args.knowledge:
        domain_knowledge = "\n".join([open(file).read() for file in args.knowledge])

    translated_srt = translate(args.input,
                               source_lang=args.source,
                               target_lang=args.target,
                               model=args.model,
                               domain_knowledge_str=domain_knowledge)

    with open(args.output, 'w') as f:
        f.write(translated_srt)


if __name__ == "__main__":
    main()
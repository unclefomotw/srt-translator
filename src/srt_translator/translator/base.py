from abc import ABC, abstractmethod

import srt


class Translator(ABC):
    @abstractmethod
    def translate(self, source_lang: str,
                  target_lang: str,
                  subtitles: list[srt.Subtitle],
                  subtitle_context: str,
                  domain_context: str) -> list[srt.Subtitle]:
        """
        Translate the given subtitles.

        :param source_lang: The language of the original subtitles.
        :param target_lang: The language to translate to.
        :param subtitles: List of srt.Subtitle objects to translate.
        :param subtitle_context: Context around the subtitles for the translator to consider.
        :param domain_context: Domain knowledge specified by the user.
        :return: List of translated srt.Subtitle objects.
        """
        pass

    @staticmethod
    def make_new_subtitles(subtitles: list[srt.Subtitle],
                           new_content: list[str]) -> list[srt.Subtitle]:
        """
        Create new srt.Subtitle objects with the given content.

        :param subtitles: List of srt.Subtitle objects to create new subtitles
        :param new_content: List of content for the new subtitles
        :return: List of new srt.Subtitle objects
        """
        new_subtitles = []
        for subtitle, content in zip(subtitles, new_content):
            new_subtitle = srt.Subtitle(index=subtitle.index,
                                        start=subtitle.start,
                                        end=subtitle.end,
                                        content=content)
            new_subtitles.append(new_subtitle)
        return new_subtitles

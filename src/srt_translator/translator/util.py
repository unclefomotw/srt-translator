def rearrange(translations: list[str], num_lines: int) -> list[str]:
    """
    Rearrange the translations to have the same number of lines as the input.

    :param translations: List of translated lines.
    :param num_lines: Number of lines in the input.
    :return: List of rearranged translations.
    """
    if len(translations) == num_lines:
        return translations

    if len(translations) < num_lines:
        new_translations = list(translations)
        for i in range(num_lines - len(translations)):
            new_translations.append(" ")
        return new_translations

    # len(translations) > num_lines
    old_len = len(translations)
    merged_translations = []
    for i in range(num_lines):
        i_start = old_len * i // num_lines
        i_end = old_len * (i + 1) // num_lines
        merged_translations.append(" ".join(translations[i_start:i_end]))
    return merged_translations
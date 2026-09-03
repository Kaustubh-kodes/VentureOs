import re
import unicodedata


class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        """
        Cleans and normalises extracted document text while preserving
        business terms, numbers, bullet structures, and paragraph boundaries.
        """
        if not text:
            return ""

        # Normalize unicode (NFKC replaces compatibility characters)
        text = unicodedata.normalize("NFKC", text)

        # Replace carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Replace non-breaking spaces and tabs with standard space
        text = text.replace("\u00a0", " ").replace("\t", " ")

        # Remove null bytes
        text = text.replace("\x00", "")

        # Collapse horizontal whitespace on lines
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]

        # Collapse more than 2 consecutive newlines into 2
        cleaned_text = "\n".join(lines)
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

        return cleaned_text.strip()


text_cleaner = TextCleaner()

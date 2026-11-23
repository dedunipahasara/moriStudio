import re
from typing import Optional

from app.ai.text_processing.vocabulary import Vocabulary


class Tokenizer:
    def __init__(
        self,
        vocabulary: Optional[Vocabulary] = None,
        max_length: int = 32,
    ):
        if max_length < 2:
            raise ValueError("max_length must be at least 2.")

        self.vocabulary = vocabulary or Vocabulary()
        self.max_length = max_length

    def tokenize(self, text: str) -> list[str]:
        if not isinstance(text, str):
            raise TypeError("Input text must be a string.")

        text = text.lower().strip()

        # Keep words, numbers and punctuation as separate tokens.
        return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)

    def build_vocabulary(
        self,
        texts: list[str],
        min_frequency: int = 1,
    ):
        tokenized_texts = [
            self.tokenize(text)
            for text in texts
        ]

        self.vocabulary.build(
            tokenized_texts,
            min_frequency=min_frequency,
        )

        return self.vocabulary

    def encode(
        self,
        text: str,
        add_special_tokens: bool = True,
        padding: bool = True,
        truncation: bool = True,
    ) -> list[int]:

        tokens = self.tokenize(text)

        token_ids = [
            self.vocabulary.token_to_index(token)
            for token in tokens
        ]

        if add_special_tokens:
            token_ids = [
                self.vocabulary.bos_id,
                *token_ids,
                self.vocabulary.eos_id,
            ]

        if truncation:
            token_ids = token_ids[:self.max_length]

            # Preserve EOS when truncating a long prompt.
            if (
                add_special_tokens
                and token_ids[-1] != self.vocabulary.eos_id
            ):
                token_ids[-1] = self.vocabulary.eos_id

        if padding:
            padding_length = self.max_length - len(token_ids)

            if padding_length > 0:
                token_ids.extend(
                    [self.vocabulary.pad_id] * padding_length
                )

        return token_ids

    def decode(
        self,
        token_ids: list[int],
        skip_special_tokens: bool = True,
    ) -> str:

        special_tokens = set(Vocabulary.SPECIAL_TOKENS)
        tokens = []

        for token_id in token_ids:
            token = self.vocabulary.index_to_token(int(token_id))

            if skip_special_tokens and token in special_tokens:
                continue

            tokens.append(token)

        text = " ".join(tokens)

        # Remove unnecessary spaces before punctuation.
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)

        return text.strip()

    def save_vocabulary(self, file_path: str):
        self.vocabulary.save(file_path)

    def load_vocabulary(self, file_path: str):
        self.vocabulary = Vocabulary.load(file_path)
        return self.vocabulary

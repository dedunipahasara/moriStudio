import json
from pathlib import Path
from collections import Counter
from typing import Iterable


class Vocabulary:
    PAD_TOKEN = "<PAD>"
    UNK_TOKEN = "<UNK>"
    BOS_TOKEN = "<BOS>"
    EOS_TOKEN = "<EOS>"

    SPECIAL_TOKENS = [
        PAD_TOKEN,
        UNK_TOKEN,
        BOS_TOKEN,
        EOS_TOKEN,
    ]

    def __init__(self):
        self.token_to_id = {
            token: index
            for index, token in enumerate(self.SPECIAL_TOKENS)
        }

        self.id_to_token = {
            index: token
            for token, index in self.token_to_id.items()
        }

    @property
    def pad_id(self):
        return self.token_to_id[self.PAD_TOKEN]

    @property
    def unk_id(self):
        return self.token_to_id[self.UNK_TOKEN]

    @property
    def bos_id(self):
        return self.token_to_id[self.BOS_TOKEN]

    @property
    def eos_id(self):
        return self.token_to_id[self.EOS_TOKEN]

    @property
    def size(self):
        return len(self.token_to_id)

    def build(
        self,
        tokenized_texts: Iterable[list[str]],
        min_frequency: int = 1,
    ):
        counter = Counter()

        for tokens in tokenized_texts:
            counter.update(tokens)

        sorted_tokens = sorted(
            [
                (token, count)
                for token, count in counter.items()
                if count >= min_frequency
                and token not in self.token_to_id
            ],
            key=lambda item: (-item[1], item[0]),
        )

        for token, _ in sorted_tokens:
            self.add_token(token)

        return self

    def add_token(self, token: str):
        if token not in self.token_to_id:
            index = len(self.token_to_id)

            self.token_to_id[token] = index
            self.id_to_token[index] = token

    def token_to_index(self, token: str) -> int:
        return self.token_to_id.get(token, self.unk_id)

    def index_to_token(self, index: int) -> str:
        return self.id_to_token.get(index, self.UNK_TOKEN)

    def save(self, file_path: str):
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "token_to_id": self.token_to_id,
            "special_tokens": self.SPECIAL_TOKENS,
        }

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    @classmethod
    def load(cls, file_path: str):
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        vocabulary = cls()

        token_to_id = data["token_to_id"]

        expected = set(cls.SPECIAL_TOKENS)
        if not expected.issubset(token_to_id):
            raise ValueError("Vocabulary is missing special tokens.")

        ids = list(token_to_id.values())

        if len(ids) != len(set(ids)):
            raise ValueError("Vocabulary contains duplicate token IDs.")

        if sorted(ids) != list(range(len(ids))):
            raise ValueError("Vocabulary IDs must be consecutive from zero.")

        vocabulary.token_to_id = token_to_id
        vocabulary.id_to_token = {
            int(index): token
            for token, index in token_to_id.items()
        }

        return vocabulary
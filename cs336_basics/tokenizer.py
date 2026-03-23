import json

class Tokenizer:
    def __init__(self, vocab, merges, special_tokens=None):
        self.vocab = vocab
        self.merges = merges
        self.special_token = special_tokens

    @classmethod
    def from_files(cls, vocab_filepath, merges_filepath, special_tokens=None):
        vocab = {}
        merges = []
        with open(vocab_filepath, "r") as vocabfile:
            vocab_str = json.load(vocabfile)
        with open(merges_filepath, "r") as mergesfile:
            merges_str = json.load(mergesfile)
        for element in vocab_str:
            vocab[int(element)] = vocab_str[element].encode("latin-1")
        for tup in merges_str:
            merges.append((tup[0].encode("latin-1"), tup[1].encode("latin-1")))

        return cls(vocab, merges, special_tokens)

#text: str
    def encode(self, text):

# iterable: iterable[str]
    def encode_iterable(self, iterable):

# ids: list[int]
    def decode(self, ids):


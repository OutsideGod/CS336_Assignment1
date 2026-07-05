import json
import regex as re

PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
BYTE_TABLE = [bytes([i]) for i in range(256)]

class Tokenizer:
    def __init__(self, vocab, merges, special_tokens=None):
        self.vocab = vocab
        self.merges = merges
        self.special_tokens = special_tokens or []
        self.inverse_vocab = {v: k for k, v in vocab.items()}
        self.inverse_merges = {pair: index for index, pair in enumerate(self.merges)}
        self.cache = {}

    @classmethod
    def from_files(cls, vocab_filepath, merges_filepath, special_tokens=None):
        def convert_vocab(pre):
            nonlocal vocab
            vocab = {int(key): value.encode("latin-1") for key, value in pre.items()}
        def convert_merges(pre):
            nonlocal merges
            for ls in pre:
                merges.append((ls[0].encode("latin-1"), ls[1].encode("latin-1")))
        vocab = {}
        merges = []
        with open(vocab_filepath, "r", encoding="utf-8") as vocabfile:
            convert_vocab(json.load(vocabfile))
        with open(merges_filepath, "r", encoding="utf-8") as mergesfile:
            convert_merges(json.load(mergesfile))
        return cls(vocab, merges, special_tokens)

#text: str
    def encode(self, text):
        def merge(tup):
            result = list(tup)
            while len(result) >= 2:
                best_pair = min(((result[i], result[i + 1]) for i in range(len(result) - 1)),key=lambda p: self.inverse_merges.get(p, float('inf')))
                if best_pair not in self.inverse_merges:
                    break

                new = []
                merged = best_pair[0] + best_pair[1]
                length = len(result)
                it = iter(range(len(result)))

                for i in it:
                    if i < length - 1 and (result[i], result[i + 1]) == best_pair:
                        new.append(merged)
                        next(it, None)
                    else:
                        new.append(result[i])
                result = new
            return result

        # Break at special tokens
        if self.special_tokens:
            sorted_specials = sorted(self.special_tokens, key=len, reverse=True)
            pat = "(" + "|".join(re.escape(t) for t in sorted_specials) + ")"
            seperated_list = re.split(pat, text)
        else:
            seperated_list = [text]

        # pretokenize + merge
        result = []
        for long_string in seperated_list:
            if long_string in self.special_tokens:
                result.append(self.inverse_vocab[long_string.encode('utf-8')])
            else:
                it = re.finditer(PAT, long_string)
                for b in it:
                    c = tuple([BYTE_TABLE[byte] for byte in b.group(0).encode('utf-8')])
                    if c not in self.cache:
                        self.cache[c] = [self.inverse_vocab[e] for e in merge(c)]
                    result.extend(self.cache[c])
        return result

# iterable: iterable[str]
    def encode_iterable(self, iterable):
        for e in iterable:
            yield from self.encode(e)

# ids: list[int]
    def decode(self, ids):
        return b"".join(self.vocab[idx] for idx in ids).decode('utf-8', errors='replace')

import json
import collections
import os
import regex as re
from multiprocessing import Pool
from functools import partial

PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
BYTE_TABLE = [bytes([i]) for i in range(256)]

class Tokenizer:
    def __init__(self, vocab, merges, special_tokens=None):
        self.vocab = vocab
        self.merges = merges
        self.special_tokens = special_tokens
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


        # Break at special tokens
        pat = "(" + "|".join(re.escape(t) for t in self.special_tokens) + ")"
        seperated_list = re.split(pat, text)

        # regex
        pre = []
        cache = {}
        for long_string in seperated_list:
            if long_string in self.special_tokens:
                pre.append(self.inverse_vocab[long_string.encode('utf-8')])
            else:
                it = re.finditer(PAT, long_string)
                for b in it:
                    c = tuple([BYTE_TABLE[byte] for byte in b.group(0).encode('utf-8')])
                    pre.append(c)
                    if c in cache:
                        pre.append(cache[c])
                    else:
                        cache[c] = merge(c)
            '''result = []
            for e in pre:
                if isinstance(e, list):
                    for string in e:
                        bytestr = string.encode('utf-8')
                        result.append([BYTE_TABLE[b] for b in bytestr])
                else:
                    result.append(e.encode('utf-8'))
            return result'''

# iterable: iterable[str]
    def encode_iterable(self, iterable):

# ids: list[int]
    def decode(self, ids):


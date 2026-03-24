import json
import collections
import os
import regex as re
from multiprocessing import Pool
from functools import partial

from cs336_basics.pretokenization_example import find_chunk_boundaries

class Tokenizer:
    def __init__(self, vocab, merges, special_tokens=None):
        self.vocab = vocab
        self.merges = merges
        self.special_tokens = special_tokens

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
        def pre_tokenize(text, i):
            #Obtain Chunk
            chunk = text[boundaries[i]:boundaries[i + 1]]

            #Break at special tokens
            pat = "(" + "|".join(re.escape(t) for t in self.special_tokens) + ")"
            seperated_list = re.split(pat, chunk)

            # regex
            PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
            pre = []
            for a in seperated_list:
                if a in self.special_tokens:
                    pre.append(a)
                else:
                    pre.extend(re.findall(PAT, a))
            result = []
            for string in pre:
                if string in self.special_tokens:
                    result.append(string.encode('utf-8'))
                else:
                    result.append([bytes([integer]) for integer in string.encode('utf-8')])
            return result
        def merge():

        def worker(text):
            merge(pre_tokenize(text))


# iterable: iterable[str]
    def encode_iterable(self, iterable):

# ids: list[int]
    def decode(self, ids):


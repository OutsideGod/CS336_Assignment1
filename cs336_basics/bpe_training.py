import collections
import os
import regex as re
from multiprocessing import Pool
from functools import partial

from cs336_basics.pretokenization_example import find_chunk_boundaries


def pretokenizer(i, input_path, boundaries, special_tokens):
    # obtain chunk
    with open(input_path, "rb") as file:
        file.seek(boundaries[i])
        chunk = file.read(boundaries[i + 1] - boundaries[i]).decode("utf-8")

    #remove special tokens
    pat = "|".join(re.escape(t) for t in special_tokens)
    seperated_list = re.split(pat, chunk)

    #pretokenize
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    counts = {}
    for a in seperated_list:
        iter = re.finditer(PAT, a)
        for b in iter:
            c = b.group(0)
            if c in counts:
                counts[c] += 1
            else:
                counts[c] = 1
    result = {}
    for str in counts:
        lst = []
        bytestr = str.encode('utf-8')
        for integer in bytestr:
            lst.append(bytes([integer]))
        tup = tuple(lst)
        result[tup] = counts[str]
    return result


def Train_bpe(input_path, vocab_size, special_tokens):

    def multi(boundaries):
        result = collections.Counter()
        worker_func = partial(
            pretokenizer,
            input_path=input_path,
            boundaries=boundaries,
            special_tokens=special_tokens
        )

        with Pool(threads) as p:
            local_result_list = p.map(worker_func, range(len(boundaries) - 1))
        for local_list in local_result_list:
            result.update(local_list)
        return result

    def merge(pre_dict, vocab_size, counter):
        nonlocal result1
        def scan(dict):
            maximum = max(dict.values())
            draw = {}
            for pair in dict:
                v = dict[pair]
                if v == maximum:
                    draw[pair] = v
            return max(draw)
        def generate(pair, counter):
            #result1
            new_vocab = pair[0] + pair[1]
            result1[counter] = new_vocab
            #result2
            return pair
        def update(pair, pre_dict, pair_dict):
            merged = pair[0] + pair[1]
            new_dict = {}
            for tup in pre_dict:
                if pair[0] not in tup or pair[1] not in tup:
                    new_dict[tup] = pre_dict[tup]
                else:
                    new_list = []
                    tupvalue = pre_dict[tup]
                    lentup = len(tup)
                    for j in range(lentup - 1):
                        a = tup[j]
                        b = tup[j + 1]
                        pair_dict[a, b] -= tupvalue
                    i = 0
                    while i < lentup:
                        a = tup[i]
                        if i + 1 == lentup:
                            new_list.append(a)
                        else:
                            b = tup[i + 1]
                            if a == pair[0] and b == pair[1]:
                                new_list.append(merged)
                                i += 1
                            else:
                                new_list.append(a)
                        i += 1
                    for i in range(len(new_list) - 1):
                        a = (new_list[i], new_list[i + 1])
                        if a in pair_dict:
                            pair_dict[a] += tupvalue
                        else:
                            pair_dict[a] = tupvalue
                    new_dict[tuple(new_list)] = pre_dict[tup]
            return new_dict, pair_dict



        merge_counter = vocab_size - len(special_tokens) - 256
        result = []
        pair_dict = {}

        #init
        for tup in pre_dict:
            for i in range(len(tup) - 1):
                a = (tup[i], tup[i + 1])
                if a in pair_dict:
                    pair_dict[a] += pre_dict[tup]
                else:
                    pair_dict[a] = pre_dict[tup]

        #merge_cycle
        while merge_counter > 0:
            #max pair
            chosen = scan(pair_dict)
            #impact
            result.append(generate(chosen, counter))
            counter += 1
            #update_both_dictionaries
            pre_dict, pair_dict = update(chosen, pre_dict, pair_dict)
            merge_counter -= 1
        return result



    #init
    result1 = {}
    counter = 0
    for i in range(len(special_tokens)):
        result1[i] = special_tokens[i].encode("utf-8")
        counter += 1
    for i in range(256):
        result1[counter] = bytes([i])
        counter += 1

    #pretokenize
    #finding boundaries
    threads = os.cpu_count() - 1
    with open(input_path, "rb") as file:
        boundaries = find_chunk_boundaries(file, threads, b"<|endoftext|>")
    #multiprocessing
    pre_dict = multi(boundaries)

    #merge
    result2 = merge(pre_dict, vocab_size, counter)

    #return
    return result1, result2
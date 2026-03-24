import time
import collections
import os
import regex as re
from multiprocessing import Pool
from functools import partial
import heapq


from cs336_basics.pretokenization_example import find_chunk_boundaries

PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
BYTE_TABLE = [bytes([i]) for i in range(256)]

def pretokenizer(i, input_path, boundaries, special_tokens):
    # obtain chunk
    with open(input_path, "rb") as file:
        file.seek(boundaries[i])
        chunk = file.read(boundaries[i + 1] - boundaries[i]).decode("utf-8")

    #remove special tokens
    pat = "|".join(re.escape(t) for t in special_tokens)
    seperated_list = re.split(pat, chunk)

    #pretokenize
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
    for string, count in counts.items():
        bytestr = string.encode('utf-8')
        tup = tuple(BYTE_TABLE[b] for b in bytestr)
        result[tup] = count
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

        class ReverseCompare:
            def __init__(self, pair):
                self.pair = pair
            def __lt__(self, other):
                return self.pair > other.pair
            def __eq__(self, other):
                return self.pair == other.pair
        nonlocal result1

        def generate(pair, counter):
            #result1
            new_vocab = pair[0] + pair[1]
            result1[counter] = new_vocab
            #result2
            return pair
        def update(pair):
            nonlocal pair_heap
            nonlocal pair_counts
            nonlocal pre_list
            nonlocal index
            a = pair[0]
            b = pair[1]
            merged = a + b

            for idx in list(index[pair]):
                sub_list = pre_list[idx]
                magni = pre_counts[idx]
                new_sub_list = []
                j = 0

                for i in range(len(sub_list) - 1):
                    a = sub_list[i]
                    b = sub_list[i + 1]
                    old_pair = (a, b)

                    pair_counts[old_pair] -= magni
                    index[old_pair].discard(idx)

                    if pair_counts[old_pair] <= 0:
                        del pair_counts[old_pair]
                        if old_pair in index:
                            del index[old_pair]
                    else:
                        heapq.heappush(pair_heap, (-pair_counts[old_pair], ReverseCompare(old_pair),old_pair))

                while j < len(sub_list):
                    f = sub_list[j]
                    if j + 1 == len(sub_list):
                        new_sub_list.append(f)
                    else:
                        s = sub_list[j + 1]
                        if f == pair[0] and s == pair[1]:
                            new_sub_list.append(merged)
                            j += 1
                        else:
                            new_sub_list.append(f)
                    j += 1

                for k in range(len(new_sub_list) - 1):
                    first = new_sub_list[k]
                    second = new_sub_list[k + 1]
                    new_pair = (first, second)
                    if new_pair in pair_counts:
                        pair_counts[new_pair] += magni
                        index[new_pair].add(idx)
                    else:
                        pair_counts[new_pair] = magni
                        index[new_pair] = {idx}
                    heapq.heappush(pair_heap, (-pair_counts[new_pair], ReverseCompare((first, second)),(first, second)))
                pre_list[idx] = new_sub_list



        pre_list = []
        pre_counts = []
        pair_counts = {}
        index = {}
        merge_counter = vocab_size - len(special_tokens) - 256
        result = []

        #init
        init_counter = 0
        for tup,freq in pre_dict.items():
            pre_list.append(list(tup))
            pre_counts.append(freq)
            for i in range(len(tup) - 1):
                a = (tup[i], tup[i + 1])
                if a in pair_counts:
                    pair_counts[a] += freq
                    index[a].add(init_counter)
                else:
                    pair_counts[a] = freq
                    index[a] = {init_counter}
            init_counter += 1
        pair_heap =[(-freq, ReverseCompare((a, b)), (a, b)) for (a, b), freq in pair_counts.items()]
        heapq.heapify(pair_heap)

        #merge_cycle
        while merge_counter > 0:
            neg_freq, _, chosen = heapq.heappop(pair_heap)
            heap_freq = -neg_freq
            #if_deleted
            if chosen not in pair_counts:
                continue
            #validation
            if heap_freq != pair_counts[chosen]:
                continue
            #impact
            result.append(generate(chosen, counter))
            counter += 1
            #update_both_dictionaries
            update(chosen)
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
    time_begin = time.time()
    threads = os.cpu_count() - 1
    with open(input_path, "rb") as file:
        boundaries = find_chunk_boundaries(file, threads, b"<|endoftext|>")
    #multiprocessing
    pre_dict = multi(boundaries)
    time_end = time.time()
    time0 = time_end - time_begin

    #merge
    time_begin = time.time()
    result2 = merge(pre_dict, vocab_size, counter)
    time_end = time.time()
    time1 = time_end - time_begin
    print("pre", time0)
    print("merge", time1)
    #return
    return result1, result2
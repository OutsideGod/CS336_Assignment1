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
    counts = {}
    pat = "|".join(re.escape(t) for t in special_tokens)

    with open(input_path, "rb") as file:
        start_pos = boundaries[i]
        end_pos = boundaries[i + 1]
        chunk_size = end_pos - start_pos

        if chunk_size < 50 * 1024 * 1024:
            file.seek(start_pos)
            chunk = file.read(chunk_size).decode("utf-8", errors="ignore")
            seperated_list = re.split(pat, chunk)
            for a in seperated_list:
                it = re.finditer(PAT, a)
                for b in it:
                    c = b.group(0)
                    counts[c] = counts.get(c, 0) + 1
        else:
            file.seek(start_pos)
            buffer = b""
            bytes_to_read = chunk_size

            while bytes_to_read > 0:
                read_size = min(10 * 1024 * 1024, bytes_to_read)
                chunk_bytes = file.read(read_size)
                if not chunk_bytes:
                    break
                bytes_to_read -= len(chunk_bytes)
                buffer += chunk_bytes

                parts = buffer.split(b"<|endoftext|>")

                buffer = parts[-1]

                for part in parts[:-1]:
                    doc = part.decode("utf-8", errors="ignore")
                    seperated_list = re.split(pat, doc)
                    for a in seperated_list:
                        it = re.finditer(PAT, a)
                        for b in it:
                            c = b.group(0)
                            counts[c] = counts.get(c, 0) + 1

            if buffer:
                doc = buffer.decode("utf-8", errors="ignore")
                seperated_list = re.split(pat, doc)
                for a in seperated_list:
                    it = re.finditer(PAT, a)
                    for b in it:
                        c = b.group(0)
                        counts[c] = counts.get(c, 0) + 1

    result = {}
    for string, count in counts.items():
        bytestr = string.encode('utf-8')
        tup = tuple(BYTE_TABLE[b] for b in bytestr)
        result[tup] = count
    return result


def Train_bpe(input_path, vocab_size, special_tokens):

    def parallel(boundaries):
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

        def generate(pair, counter):
            #result1
            new_vocab = pair[0] + pair[1]
            result1[counter] = new_vocab
            #result2
            return pair
        def update(pair):
            def remove_old(old_pair):
                if old_pair == pair:
                    return
                pair_changes[old_pair] -= magni
                #pair_counts[old_pair] -= magni
                #if pair_counts[old_pair] <= 0:
                    #pair_counts.pop(old_pair, None)
                    #index.pop(old_pair, None)
                #else:
                    #heapq.heappush(pair_heap, (-pair_counts[old_pair], ReverseCompare(old_pair), old_pair))

            def add_new(new_pair):
                pair_changes[new_pair] += magni
                index[new_pair].append(idx)
                #if new_pair in pair_counts:
                    #pair_counts[new_pair] += magni
                    #index[new_pair].append(idx)
                #else:
                    #pair_counts[new_pair] = magni
                    #index[new_pair] = [idx]
                #heapq.heappush(pair_heap, (-pair_counts[new_pair], ReverseCompare(new_pair), new_pair))

            a , b = pair
            merged = a + b
            pair_changes = collections.defaultdict(int)
            for idx in set(index[pair]):
                sub_list = pre_list[idx]
                magni = pre_counts[idx]
                i = 0
                j = 0
                pos = []

                #locating the merged pair's position
                while i < len(sub_list) - 1:
                    if sub_list[i] == a and sub_list[i + 1] == b:
                        pos.append(i)
                        i += 2
                    else:
                        i += 1
                if not pos:
                    continue

                #delete the old pairs
                no_more_old = set()
                for e in pos:
                    if e > 0:
                        if e - 1 not in no_more_old:
                            no_more_old.add(e - 1)
                            old_left = (sub_list[e - 1], a)
                            remove_old(old_left)
                    if e < len(sub_list) - 2:
                        if e + 1 not in no_more_old:
                            no_more_old.add(e + 1)
                            old_right = (b, sub_list[e + 2])
                            remove_old(old_right)

                #create merged sublist
                new_sub_list = []
                new_pos = []
                while j < len(sub_list):
                    if j < len(sub_list) - 1 and sub_list[j] == a and sub_list[j + 1] == b:
                        new_pos.append(len(new_sub_list))
                        new_sub_list.append(merged)
                        j += 2
                    else:
                        new_sub_list.append(sub_list[j])
                        j += 1

                #add the new pairs
                no_more_new = set()
                for e in new_pos:
                    if e > 0:
                        if e - 1 not in no_more_new:
                            no_more_new.add(e - 1)
                            new_left = (new_sub_list[e - 1], merged)
                            add_new(new_left)
                    if e < len(new_sub_list) - 1:
                        if e not in no_more_new:
                            no_more_new.add(e)
                            new_right = (merged, new_sub_list[e + 1])
                            add_new(new_right)
                pre_list[idx] = new_sub_list
            for p, c in pair_changes.items():
                if p == pair:
                    continue
                pair_counts[p] = pair_counts.get(p, 0) + c
                if pair_counts[p] <= 0:
                    pair_counts.pop(p, None)
                    index.pop(p, None)
                else:
                    heapq.heappush(pair_heap, (-pair_counts[p], ReverseCompare(p), p))
            pair_counts.pop(pair, None)
            index.pop(pair, None)


        pre_list = []
        pre_counts = []
        pair_counts = {}
        index = collections.defaultdict(list)
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
                    index[a].append(init_counter)
                else:
                    pair_counts[a] = freq
                    index[a] = [init_counter]
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
    threads = os.cpu_count() - 1
    with open(input_path, "rb") as file:
        boundaries = find_chunk_boundaries(file, threads, b"<|endoftext|>")
    #multiprocessing
    pre_dict = parallel(boundaries)

    #merge
    result2 = merge(pre_dict, vocab_size, counter)
    #return
    return result1, result2
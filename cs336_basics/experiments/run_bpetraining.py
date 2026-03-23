from cs336_basics.bpe_training import Train_bpe
import json
import time

def trans_vocab(vocab):
    n_vocab = {}
    for index in vocab:
        n_vocab[index] = vocab[index].decode("latin-1")
    return n_vocab

def trans_merges(merges):
    n_merges = []
    for t in merges:
        a = t[0].decode("latin-1")
        b = t[1].decode("latin-1")
        n_merges.append((a, b))
    return n_merges

def save(x, output_path):
    if type(x) == dict:
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(trans_vocab(x), file, ensure_ascii=False, indent=4)
    else:
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(trans_merges(x), file, ensure_ascii=False, indent=4)


def general(input_path, output_path1, output_path2, vocab_size, special_tokens):
    vocab, merges = Train_bpe(input_path, vocab_size, special_tokens)
    save(vocab, output_path1)
    save(merges, output_path2)


input_path0 = r"/home/ydy11/CS336/Assignment1/data/TinyStoriesV2-GPT4-train.txt"
output_path0_0 = r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/TinyStories_vocab.json"
output_path0_1 = r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/TinyStories_merges.json"

input_path1 = r"/home/ydy11/CS336/Assignment1/data/owt_train.txt"
output_path1_0 = r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/owt_vocab.json"
output_path1_1 = r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/owt_merges.json"

time_begin = time.time()
general(input_path0, output_path0_0, output_path0_1, 10000, ["<|endoftext|>"])
time_end = time.time()
time0 = time_end - time_begin

#time_begin = time.time()
#general(input_path1, output_path1_0, output_path1_1, 32000, ["<|endoftext|>"])
#time_end = time.time()
#time1 = time_end - time_begin

print(time0)#, " ", time1)
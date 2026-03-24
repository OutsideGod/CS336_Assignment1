from cs336_basics.bpe_training import Train_bpe
import json
import time

def general(input_path, output_path1, output_path2, vocab_size, special_tokens):
    vocab, merges = Train_bpe(input_path, vocab_size, special_tokens)
    with open(output_path1, "w", encoding="utf-8") as file:
        json.dump({index : value.decode("latin-1") for index, value in vocab.items()}, file, ensure_ascii=False, indent=4)
    with open(output_path2, "w", encoding="utf-8") as file:
        json.dump([(a.decode("latin-1"), b.decode("latin-1")) for a, b in merges], file, ensure_ascii=False, indent=4)

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

print("结束", time0)#, " ", time1)
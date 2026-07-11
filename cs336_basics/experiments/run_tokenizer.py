from cs336_basics.tokenizer import Tokenizer
import time

def sample_documents(file_path, num_docs=10):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        docs = [d.strip() for d in content.split("<|endoftext|>") if d.strip()]
    return docs[:num_docs]

ts_tokenizer = Tokenizer.from_files(r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/TinyStories_vocab.json", r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/TinyStories_merges.json")
owt_tokenizer = Tokenizer.from_files(r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/owt_vocab.json", r"/home/ydy11/CS336/Assignment1/cs336_basics/saves/owt_merges.json")

def calculate_ratio(docs, tokenizer, name):
    total_bytes = 0
    total_tokens = 0

    for idx, doc in enumerate(docs):
        doc_bytes = len(doc.encode("utf-8"))
        token_ids = tokenizer.encode(doc)
        doc_tokens = len(token_ids)

        total_bytes += doc_bytes
        total_tokens += doc_tokens

    compression_ratio = total_bytes / total_tokens

    print(f"{name}")
    print(f"{total_bytes} Bytes")
    print(f"{total_tokens} Tokens")
    print(f"Compression rate: {compression_ratio:.4f} bytes/token\n")

    return compression_ratio

time_begin = time.time()
calculate_ratio(sample_documents(r"/home/ydy11/CS336/Assignment1/data/owt_valid.txt"), ts_tokenizer, "tiny_story")
calculate_ratio(sample_documents(r"/home/ydy11/CS336/Assignment1/data/owt_valid.txt"), owt_tokenizer, "tiny_story")
time_end = time.time()
time0 = time_end - time_begin
print("用时", time0)
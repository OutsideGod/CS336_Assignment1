import math
import torch
import torch.nn as nn
from einops import einsum
from einops import reduce

class Linear(nn.Module):
    def __init__(self, in_features, out_features, device=None, dtype=None):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.W = nn.Parameter(torch.empty(out_features, in_features, device=device, dtype=dtype))
        std = math.sqrt(2.0 / (in_features + out_features))
        nn.init.trunc_normal_(self.W, mean = 0.0, std = std, a = -3.0 * std, b = 3.0 * std)

    def forward(self, x: torch.Tensor):
        return einsum(self.W, x, 'out in, ... in -> ... out')


class Embedding(nn.Module):
    def __init__(self, num_embeddings, embedding_dim, device=None, dtype=None):
        super().__init__()
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.E = nn.Parameter(torch.empty(num_embeddings, embedding_dim, device=device, dtype=dtype))
        nn.init.trunc_normal_(self.E, mean = 0.0, std = 1.0, a = -3.0, b = 3.0)

    def forward(self, token_ids: torch.Tensor):
        return self.E[token_ids]

class RMSNorm(nn.Module):
    def __init__(self, d_model, eps = 1e-5, device=None, dtype=None):
        super().__init__()
        self.d_model = d_model
        self.eps = eps
        self.G = nn.Parameter(torch.ones(d_model, device=device, dtype=dtype))
    def forward(self, x: torch.Tensor):
        in_dtype = x.dtype
        x = x.to(torch.float32)
        base = torch.sqrt(reduce(x ** 2, "batch sequence dmodel -> batch sequence 1", "mean") + self.eps)
        result = x * self.G / base
        return result.to(in_dtype)
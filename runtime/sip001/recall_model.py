"""
The recall pathway's backbone -- identical architecture to Benchmark A /
EXP-018's CausalTransformerLM, re-declared here per this program's per-
artifact self-containment convention. Class A mechanism (the Transformer
and its training loop are validated engineering); the memory policy that
sits on top of it is Class B (memory.py, EXP-018's known limitation).
"""

import torch
import torch.nn as nn

D_MODEL, N_HEAD, N_LAYERS, FFN_DIM = 128, 4, 4, 256


class CausalTransformerLM(nn.Module):
    def __init__(self, vocab_size, seq_len):
        super().__init__()
        self.tok_embed = nn.Embedding(vocab_size, D_MODEL)
        self.pos_embed = nn.Embedding(seq_len, D_MODEL)
        layer = nn.TransformerEncoderLayer(D_MODEL, N_HEAD, FFN_DIM, batch_first=True, activation='gelu')
        self.encoder = nn.TransformerEncoder(layer, N_LAYERS)
        self.ln_out = nn.LayerNorm(D_MODEL)
        self.lm_head = nn.Linear(D_MODEL, vocab_size)
        causal_mask = torch.triu(torch.ones((seq_len, seq_len), dtype=torch.bool), diagonal=1)
        self.register_buffer('causal_mask', causal_mask)

    def forward(self, tokens):
        B, T = tokens.shape
        pos = torch.arange(T, device=tokens.device).unsqueeze(0).expand(B, T)
        h = self.tok_embed(tokens) + self.pos_embed(pos)
        h = self.encoder(h, mask=self.causal_mask[:T, :T])
        h = self.ln_out(h)
        return self.lm_head(h)

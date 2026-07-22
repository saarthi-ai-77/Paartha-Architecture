"""
ACA-MVP-001, Benchmark B, Generic Baseline: a real encoder-decoder
Transformer, trained end-to-end on the real SCAN addprim_jump split, with NO
hand-specified compositional structure. Must discover both the primitive-to-
action mapping AND the compositional rules (repetition, and/after ordering,
direction turns) purely from the 14,670 training examples.

Metric is standard SCAN exact-sequence-match accuracy (not per-token), so
this is directly comparable to Lake & Baroni (2018)'s own published numbers
for this exact split (~1% reported there for vanilla seq2seq RNNs) and to
the broader compositional-generalization literature's replications with
Transformer seq2seq models (also near-zero on this split).

Data: real, downloaded, byte-for-byte from
https://github.com/brendenlake/SCAN (add_prim_split/tasks_{train,test}_addprim_jump.txt).
Grammar used only to load pairs -- this model does NOT use scan_common's
parser/interpreter at all, by design (that is exactly the structure being
withheld from this baseline).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import time

from scan_common import load_pairs

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device: {device}")

IN_VOCAB = ["<pad>", "walk", "look", "run", "jump", "turn", "left", "right",
            "opposite", "around", "twice", "thrice", "and", "after"]
IN_STOI = {w: i for i, w in enumerate(IN_VOCAB)}
IN_PAD = IN_STOI["<pad>"]

OUT_VOCAB = ["<pad>", "<bos>", "<eos>", "I_WALK", "I_LOOK", "I_RUN", "I_JUMP", "I_TURN_LEFT", "I_TURN_RIGHT"]
OUT_STOI = {w: i for i, w in enumerate(OUT_VOCAB)}
OUT_PAD, OUT_BOS, OUT_EOS = OUT_STOI["<pad>"], OUT_STOI["<bos>"], OUT_STOI["<eos>"]


def encode_in(tokens):
    return [IN_STOI[t] for t in tokens]


def encode_out(tokens):
    return [OUT_BOS] + [OUT_STOI[t] for t in tokens] + [OUT_EOS]


D_MODEL = 128
N_HEAD = 4
ENC_LAYERS = 2
DEC_LAYERS = 2
FFN_DIM = 256
MAX_OUT_LEN = 50  # verified max real output length is 48 (+bos/eos = 50)


class Seq2SeqTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.src_tok = nn.Embedding(len(IN_VOCAB), D_MODEL, padding_idx=IN_PAD)
        self.src_pos = nn.Embedding(64, D_MODEL)
        self.tgt_tok = nn.Embedding(len(OUT_VOCAB), D_MODEL, padding_idx=OUT_PAD)
        self.tgt_pos = nn.Embedding(MAX_OUT_LEN + 2, D_MODEL)
        enc_layer = nn.TransformerEncoderLayer(D_MODEL, N_HEAD, FFN_DIM, batch_first=True, activation='gelu')
        self.encoder = nn.TransformerEncoder(enc_layer, ENC_LAYERS)
        dec_layer = nn.TransformerDecoderLayer(D_MODEL, N_HEAD, FFN_DIM, batch_first=True, activation='gelu')
        self.decoder = nn.TransformerDecoder(dec_layer, DEC_LAYERS)
        self.out_proj = nn.Linear(D_MODEL, len(OUT_VOCAB))

    def encode(self, src, src_pad_mask):
        pos = torch.arange(src.size(1), device=src.device).unsqueeze(0)
        h = self.src_tok(src) + self.src_pos(pos)
        return self.encoder(h, src_key_padding_mask=src_pad_mask)

    def decode_step(self, tgt, memory, src_pad_mask):
        pos = torch.arange(tgt.size(1), device=tgt.device).unsqueeze(0)
        h = self.tgt_tok(tgt) + self.tgt_pos(pos)
        causal_mask = torch.triu(torch.ones((tgt.size(1), tgt.size(1)), dtype=torch.bool, device=tgt.device), diagonal=1)
        tgt_pad_mask = (tgt == OUT_PAD)
        h = self.decoder(h, memory, tgt_mask=causal_mask, tgt_key_padding_mask=tgt_pad_mask,
                          memory_key_padding_mask=src_pad_mask)
        return self.out_proj(h)

    def forward(self, src, tgt_in, src_pad_mask):
        memory = self.encode(src, src_pad_mask)
        return self.decode_step(tgt_in, memory, src_pad_mask)


def param_count(m):
    return sum(p.numel() for p in m.parameters())


def pad_batch(seqs, pad_val):
    maxlen = max(len(s) for s in seqs)
    return [s + [pad_val] * (maxlen - len(s)) for s in seqs]


def make_batch(pairs, device):
    src = [encode_in(i) for i, o in pairs]
    tgt = [encode_out(o) for i, o in pairs]
    src_t = torch.tensor(pad_batch(src, IN_PAD), dtype=torch.long, device=device)
    tgt_t = torch.tensor(pad_batch(tgt, OUT_PAD), dtype=torch.long, device=device)
    return src_t, tgt_t


BATCH_SIZE = 128
EPOCHS = 25
LR = 3e-4


def train_one_seed(train_pairs, test_pairs, seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    model = Seq2SeqTransformer().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    n = len(train_pairs)
    steps = 0

    for epoch in range(EPOCHS):
        order = rng.permutation(n)
        for start in range(0, n, BATCH_SIZE):
            idx = order[start:start + BATCH_SIZE]
            batch = [train_pairs[i] for i in idx]
            src, tgt = make_batch(batch, device)
            src_pad_mask = (src == IN_PAD)
            tgt_in, tgt_out = tgt[:, :-1], tgt[:, 1:]
            logits = model(src, tgt_in, src_pad_mask)
            loss = F.cross_entropy(logits.reshape(-1, len(OUT_VOCAB)), tgt_out.reshape(-1), ignore_index=OUT_PAD)
            opt.zero_grad(); loss.backward(); opt.step()
            steps += 1

    train_acc = evaluate(model, train_pairs[:2000], device)  # subsample for speed; sanity check only
    test_acc = evaluate(model, test_pairs, device)
    return model, steps, train_acc, test_acc


@torch.no_grad()
def evaluate(model, pairs, device, batch_size=256):
    model.eval()
    correct = 0
    for start in range(0, len(pairs), batch_size):
        batch = pairs[start:start + batch_size]
        src = [encode_in(i) for i, o in batch]
        src_t = torch.tensor(pad_batch(src, IN_PAD), dtype=torch.long, device=device)
        src_pad_mask = (src_t == IN_PAD)
        memory = model.encode(src_t, src_pad_mask)
        B = len(batch)
        generated = torch.full((B, 1), OUT_BOS, dtype=torch.long, device=device)
        finished = torch.zeros(B, dtype=torch.bool, device=device)
        for _ in range(MAX_OUT_LEN + 1):
            logits = model.decode_step(generated, memory, src_pad_mask)
            next_tok = logits[:, -1, :].argmax(dim=-1)
            next_tok = torch.where(finished, torch.full_like(next_tok, OUT_PAD), next_tok)
            generated = torch.cat([generated, next_tok.unsqueeze(1)], dim=1)
            finished = finished | (next_tok == OUT_EOS)
            if finished.all():
                break
        gen_list = generated[:, 1:].cpu().tolist()  # drop BOS
        for g, (i, o) in zip(gen_list, batch):
            if OUT_EOS in g:
                g = g[:g.index(OUT_EOS)]
            pred_str = [OUT_VOCAB[t] for t in g]
            correct += int(pred_str == o)
    model.train()
    return correct / len(pairs)


SEEDS = range(5)


def main():
    t0 = time.time()
    train_pairs = load_pairs("tasks_train_addprim_jump.txt")
    test_pairs = load_pairs("tasks_test_addprim_jump.txt")
    print(f"train={len(train_pairs)} test={len(test_pairs)}")

    results = []
    n_params = None
    for seed in SEEDS:
        model, steps, train_acc, test_acc = train_one_seed(train_pairs, test_pairs, seed)
        n_params = param_count(model)
        print(f"seed {seed}: steps={steps} train_acc(subsample)={train_acc:.4f} test_acc(exact-match)={test_acc:.4f}")
        results.append({"seed": seed, "train_acc_subsample": train_acc, "test_acc": test_acc})

    test_accs = [r["test_acc"] for r in results]
    print(f"\nModel parameter count: {n_params}")
    print(f"SUMMARY generic_seq2seq: test_acc={np.mean(test_accs):.4f}+/-{np.std(test_accs):.4f}")

    out = {
        "meta": {"model": "generic_seq2seq_transformer", "epochs": EPOCHS, "batch_size": BATCH_SIZE,
                 "d_model": D_MODEL, "n_head": N_HEAD, "enc_layers": ENC_LAYERS, "dec_layers": DEC_LAYERS,
                 "param_count": n_params, "seeds": list(SEEDS), "elapsed_sec": time.time() - t0},
        "summary": {"test_acc_mean": float(np.mean(test_accs)), "test_acc_std": float(np.std(test_accs))},
        "raw": results,
    }
    with open("results_generic_seq2seq.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote results_generic_seq2seq.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()

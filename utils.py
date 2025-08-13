import os
import re, math
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt

CTA_PATTERNS = [
    r"\bbuy\b",
    r"\bpurchase\b",
    r"\bshop\b",
    r"\blearn more\b",
    r"\bsign\s*up\b",
    r"\bget started\b",
    r"\btry (it|now)\b",
    r"\badd to cart\b",
    r"\border\b",          # catches "order now", "order today", "order your..."
    r"\bsubscribe\b",
    r"\bbook\b",
    r"\bgrab\b",           # e.g., "grab yours now"
    r"\bclaim\b",          # e.g., "claim your free trial"
    r"\bstart\b",          # e.g., "start saving today"
    r"\bjoin\b"            # e.g., "join now", "join the club"
]
def has_cta(text: str) -> bool:
    """
    Returns True if the text contains a recognizable Call-To-Action phrase.
    Matching is case-insensitive and flexible to catch variations.
    """
    t = text.lower()
    return any(re.search(p, t) for p in CTA_PATTERNS)

def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))

def sentence_count(text: str) -> int:
    # Simple proxy
    return max(1, len(re.findall(r"[.!?]+", text)))

def syllable_count(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)

def flesch_reading_ease(text: str) -> float:
    words = re.findall(r"\b\w+\b", text)
    if not words:
        return 0.0
    syllables = sum(syllable_count(w) for w in words)
    sentences = sentence_count(text)
    W, S, Y = len(words), sentences, syllables
    return 206.835 - 1.015 * (W / S) - 84.6 * (Y / W)

def length_fit_score(text: str, target: str) -> float:
    w = word_count(text)
    if target == "short":
        # Ideal <= 25 words
        ideal = 20
    elif target == "medium":
        ideal = 60
    else:
        ideal = 110
    return max(0.0, 1.0 - abs(w - ideal) / (ideal + 1e-9))

def quality_score(text: str, target_length: str) -> float:
    fre = flesch_reading_ease(text)
    cta_bonus = 0.15 if has_cta(text) else 0.0
    length_fit = length_fit_score(text, target_length)
    # Normalize Flesch (0..100) to 0..1
    fre_n = max(0.0, min(1.0, fre / 100.0))
    return 0.5 * fre_n + 0.35 * length_fit + cta_bonus

def prob_click_from_score(score: float) -> float:
    # Map score (0..1) to probability (sigmoid)
    return 1 / (1 + math.exp(- (score * 6 - 3)))  # centered ~0.5 at score=0.5

def ab_simulate(p_A: float, p_B: float, n: int = 1000) -> Dict[str, float]:
    import random
    conv_A = sum(1 for _ in range(n) if random.random() < p_A)
    conv_B = sum(1 for _ in range(n) if random.random() < p_B)
    rate_A = conv_A / n
    rate_B = conv_B / n
    lift = (rate_B - rate_A) / (rate_A + 1e-9)
    # Two-proportion z-test (approx.)
    p_pool = (conv_A + conv_B) / (2 * n)
    se = math.sqrt(p_pool * (1 - p_pool) * (2 / n))
    z = (rate_B - rate_A) / (se + 1e-9)
    return {"rate_A": rate_A, "rate_B": rate_B, "lift": lift, "z": z, "conv_A": conv_A, "conv_B": conv_B}

def plot_lift(result: Dict[str, float]):
    # Simple bar chart without specifying colors
    labels = ["A", "B"]
    values = [result["rate_A"], result["rate_B"]]
    plt.figure()
    plt.bar(labels, values)
    plt.title("Simulated Conversion Rates")
    plt.ylabel("Rate")
    return plt.gcf()

def save_run_to_csv(inputs: Dict, outputs, path: str):
    rows = []
    for i, out in enumerate(outputs, 1):
        row = inputs.copy()
        row.update({"variant": f"V{i}", "copy": out})
        rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        if not os.path.exists(path):
            df.to_csv(path, index=False)
        else:
            df.to_csv(path, mode="a", header=False, index=False)
# Full utils.py code here from earlier generation

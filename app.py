import os, random
import streamlit as st
import pandas as pd

# --- Optional .env support (won't error if python-dotenv isn't installed) ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from openai import OpenAI
from prompts import (
    SYSTEM_BASE,
    build_draft_prompt,
    build_style_polish_prompt,
    build_length_prompt,
    STYLE_GUIDE,
)
from utils import (
    quality_score,
    prob_click_from_score,
    ab_simulate,
    plot_lift,
    save_run_to_csv,
    has_cta,
)

st.set_page_config(page_title="Marketing Copy Generator", page_icon="📝", layout="wide")

# --- Sidebar: Config ---
st.sidebar.header("Configuration")
model = st.sidebar.text_input("OpenAI model", value="gpt-4o-mini")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
max_tokens = st.sidebar.slider("Max tokens", 100, 800, 280, 20)
log_path = st.sidebar.text_input("Log CSV path", value="runs_log.csv")
st.sidebar.caption("Set OPENAI_API_KEY in your environment or a .env file.")

# Create the client (will raise if no key present)
client = OpenAI()  # or OpenAI(api_key="sk-...")

st.title("📝 Marketing Copy Generator with Style Selector")
st.caption("Generate ad copy, social captions, or product descriptions in a selected tone, then run a quick A/B test.")

# --- Helpers ---
def load_sample_row():
    df = pd.read_csv("sample_product.csv",sep=",",quotechar='"',         # handle commas inside quotes
        skipinitialspace=True )
    row = df.iloc[random.randint(0, len(df) - 1)]
    return {k: str(v) for k, v in row.items()}

# --- Load sample expander ---
with st.expander("Load Sample Product Row"):
    if st.button("Load a sample"):
        sample = load_sample_row()
        print(sample)
        st.session_state["product_name"] = str(sample.get("product_name", "") or "")
        st.session_state["brand"] = str(sample.get("brand", "") or "")
        st.session_state["price"] = str(sample.get("price", "") or "")
        st.session_state["audience"] = str(sample.get("audience", "") or "")
        st.session_state["features"] = str(sample.get("features", "") or "")
        st.session_state["benefits"] = str(sample.get("benefits", "") or "")
        st.session_state["keywords"] = str(sample.get("keywords", "") or "")

# --- Normalize session state to strings to avoid Streamlit TypeError ---
for k in ["product_name", "brand", "price", "audience", "features", "benefits", "keywords"]:
    if k not in st.session_state or st.session_state[k] is None:
        st.session_state[k] = ""
    else:
        st.session_state[k] = str(st.session_state[k])

# --- Inputs ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    kind = st.selectbox("Content Type", ["Ad copy", "Social caption", "Product description"])
    style = st.selectbox("Style / Tone", list(STYLE_GUIDE.keys()), index=2)  # default persuasive
    length = st.selectbox("Length", ["short", "medium", "long"], index=1)
with col2:
    product_name = st.text_input("Product Name", key="product_name")
    brand = st.text_input("Brand", key="brand")
    price = st.text_input("Price (optional)", key="price")
with col3:
    audience = st.text_input("Audience (who is this for?)", key="audience")
    guidelines = st.text_area("Brand Guidelines (optional)", placeholder="Voice, do/don'ts, banned phrases…")

features = st.text_area(
    "Features (semicolon-separated)",
    key="features",
    placeholder="e.g., BPA-free; Double-wall; Keeps cold 24h",
)
benefits = st.text_area(
    "Benefits (semicolon-separated)",
    key="benefits",
    placeholder="e.g., Healthier hydration; No plastic taste",
)
keywords = st.text_input("Keywords (comma-separated)", key="keywords", placeholder="eco, hydration, bottle")

# --- OpenAI helper ---
def call_openai(messages):
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()

def make_variants(n=3):
    _features = str(features or "")
    _benefits = str(benefits or "")
    _keywords = str(keywords or "")

    feats = [s.strip() for s in _features.split(";") if s.strip()]
    bens = [s.strip() for s in _benefits.split(";") if s.strip()]
    keys = [s.strip() for s in _keywords.split(",") if s.strip()]
    product = {"product_name": product_name, "brand": brand, "price": price}

    base_messages = [
        {
            "role": "system",
            "content": SYSTEM_BASE
            + (f" Also follow these brand notes: {guidelines}" if guidelines else ""),
        },
        {"role": "user", "content": build_draft_prompt(kind, product, audience, feats, bens, keys)},
    ]
    draft = call_openai(base_messages)

    style_messages = base_messages + [
        {"role": "assistant", "content": draft},
        {"role": "user", "content": build_style_polish_prompt(style)},
    ]
    styled = call_openai(style_messages)

    length_messages = style_messages + [
        {"role": "assistant", "content": styled},
        {"role": "user", "content": build_length_prompt(length)},
    ]
    final = call_openai(length_messages)

    # Ask for two alternates to reach 3 total variants
    alt_messages = length_messages + [
        {"role": "assistant", "content": final},
        {
            "role": "user",
            "content": "Now provide two alternative phrasings that keep the same facts, tone, and length targets. "
            "Return each variant separated by a line with three dashes (---). No explanations.",
        },
    ]
    alts = call_openai(alt_messages)
    variants = [v.strip() for v in (final + "\n---\n" + alts).split("---") if v.strip()]
    return variants[:3]

# --- Generate ---
if st.button("Generate Copy"):
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY not set. Add it to your environment or a .env file.")
    else:
        variants = make_variants(n=3)
        st.session_state["variants"] = variants

        # Log
        inputs = {
            "kind": kind,
            "style": style,
            "length": length,
            "product_name": product_name,
            "brand": brand,
            "price": price,
            "audience": audience,
            "features": features,
            "benefits": benefits,
            "keywords": keywords,
            "guidelines": guidelines,
        }
        save_run_to_csv(inputs, variants, log_path)

# --- Output + A/B ---
variants = st.session_state.get("variants", [])

if variants:
    st.subheader("Generated Variants")
    cols = st.columns(3)
    for i, v in enumerate(variants):
        with cols[i % 3]:
            st.text_area(f"Variant V{i+1}", v, height=200, key=f"var_{i+1}")
            st.write(f"CTA detected: **{'Yes' if has_cta(v) else 'No'}**")
            st.write(f"Quality score (heuristic): **{quality_score(v, length):.2f}**")

    st.divider()
    st.subheader("A/B Test (Simulated)")
    colA, colB = st.columns(2)
    all_opts = [f"V{i+1}" for i in range(len(variants))]
    with colA:
        pickA = st.selectbox("Choose A", all_opts, index=0)
    with colB:
        pickB = st.selectbox("Choose B", all_opts, index=min(1, len(all_opts) - 1))

    length_target = st.selectbox(
        "Target length for scoring", ["short", "medium", "long"], index=["short", "medium", "long"].index(length)
    )
    n_users = st.slider("Simulated users", 100, 5000, 1000, 100)

    if st.button("Run A/B Simulation"):
        A = variants[all_opts.index(pickA)]
        B = variants[all_opts.index(pickB)]
        sA = quality_score(A, length_target)
        sB = quality_score(B, length_target)
        pA = prob_click_from_score(sA)
        pB = prob_click_from_score(sB)
        res = ab_simulate(pA, pB, n=n_users)

        st.write(
            {
                "score_A": round(sA, 3),
                "score_B": round(sB, 3),
                "p_A": round(pA, 3),
                "p_B": round(pB, 3),
                "rate_A": round(res["rate_A"], 3),
                "rate_B": round(res["rate_B"], 3),
                "lift_%": round(res["lift"] * 100, 2),
                "z_score": round(res["z"], 2),
            }
        )
        fig = plot_lift(res)
        st.pyplot(fig)
else:
    st.info("Generate copy to see variants and A/B test options.")

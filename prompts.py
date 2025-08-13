from typing import List, Dict

SYSTEM_BASE = (
    "You are a concise, brand-safe marketing copywriter. "
    "Always keep claims truthful, avoid prohibited content, and be respectful. "
    "Assume the user provided accurate product facts and do not invent specs."
)

STYLE_GUIDE = {
    "witty": "Clever wordplay, light humor, snappy rhythm. Avoid sarcasm that could offend.",
    "formal": "Professional, clear, and respectful tone. Avoid slang. Use complete sentences.",
    "persuasive": "Benefit-led, confident language, clear call-to-action. Avoid hype or unverifiable claims.",
    "friendly": "Warm, approachable, reassuring. Use everyday language, short sentences.",
    "bold": "High-energy, punchy lines, strong verbs. Keep it positive and tasteful.",
    "luxury": "Elegant, refined, sensory detail. Focus on craftsmanship and exclusivity.",
    "playful": "Fun, upbeat, whimsical touches. Keep it concise and accessible.",
    "empathetic": "Supportive, understanding, people-first. Avoid judgmental phrases.",
    "minimalist": "Spare, crisp, essential words only. No fluff."
}

LENGTH_NOTES = {
    "short": "Aim for 1–2 sentences or under 140 characters when possible.",
    "medium": "Aim for 3–5 concise sentences.",
    "long": "Aim for a short paragraph of 6–8 sentences."
}

def build_draft_prompt(kind: str, product: Dict, audience: str, features: List[str], benefits: List[str], keywords: List[str]) -> str:
    return f"""
    Create a **{kind}** draft grounded only in the facts below. No style flourishes yet, keep it neutral and benefit-led.

    Product:
    - Name: {product.get('product_name','')}
    - Brand: {product.get('brand','')}
    - Price: {product.get('price','')}

    Audience: {audience}

    Key features:
    - {'; '.join(features)}

    Customer benefits:
    - {'; '.join(benefits)}

    SEO/keywords to naturally weave in: {', '.join(keywords)}

    Constraints:
    - No medical/guaranteed performance claims.
    - Be specific and concrete; do not invent specs.
    - One clear call-to-action at the end.
    """

def build_style_polish_prompt(style: str) -> str:
    return f"""
    Rewrite the draft to match this tone: **{style}**.
    Style guidance: {STYLE_GUIDE.get(style, 'Clear and concise.')}
    Keep factual content intact.
    """

def build_length_prompt(length: str) -> str:
    return f"""
    Normalize the length to **{length}**.
    {LENGTH_NOTES.get(length, '')}
    Keep the CTA; keep it skimmable.
    Return only the final copy, no explanations.
    """
# Full prompts.py code here from earlier generation

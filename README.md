# Marketing Copy Generator with Style Selector (Streamlit, Python 3.12)

A hands-on demo app that generates marketing copy (ad copy, social captions, product descriptions) in a selectable style,
and lets you run quick A/B tests on the generated variants.

What we’ll build: 
1. Copy generator
2. Style selector 
3. Quick A/B test 

   (https://www.optimizely.com/optimization-glossary/ab-testing/)

   (https://www.youtube.com/watch?v=WRGW6xHLy3k)

Skills: style conditioning, prompt chaining, lightweight experimentation

## Quickstart

1) Create a virtual env (Python 3.12) and install deps:
```
pip install -r requirements.txt
```

2) Set your OpenAI key as an env var:
```
OPENAI_API_KEY="sk-..."
```

3) Run the app:
```
streamlit run app.py
```

## Features
Prompt chaining:

Draft (grounded in inputs)

Style polish (witty/formal/persuasive/etc.)

Length normalization (short/medium/long)

Simulated A/B test converts a heuristic quality score to a click probability and runs a two-proportion z-test.

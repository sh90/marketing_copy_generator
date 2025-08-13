# Marketing Copy Generator with Style Selector 

A hands-on demo app that generates marketing copy (ad copy, social captions, product descriptions) in a selectable style,
and lets you run quick A/B tests on the generated variants.

What we’ll build: 
1. Copy generator
2. Style selector 
3. Quick A/B test 

   (https://www.optimizely.com/optimization-glossary/ab-testing/)

   (https://www.youtube.com/watch?v=WRGW6xHLy3k)

```
What is A/B Testing & How We’re Using It Today

1. What is A/B Testing?
   Definition: A method to compare two or more versions of something to see which performs better.
   
   Goal: Make decisions based on data, not guesswork.

2. How it works:

   Show Version A to one group of users
   
   Show Version B to another group
   
   Measure which one achieves your goal better (e.g., clicks, sign-ups, sales)

3. Why It’s Useful in Marketing
   Removes personal bias — lets the audience decide
   
   Measures the impact of changes (e.g., adding a CTA, changing tone)
   
   Optimizes for conversion rate and ROI

4. How It’s Helping in This Demo
   We’re generating two different marketing copies using GPT-4o-mini
   
   Each version may vary in:
   
   Tone/Style (witty, formal, persuasive)
   
   CTA presence
   
   We simulate showing these to different “audiences”
   
   We then track & compare the click-through rate (CTR) to find the winner

5.Key takeaway:
   A/B testing is like a taste test — you let the customer decide which flavor they like best, then use that to guide your next move.
   ```
   
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
```Prompt chaining```

```Draft (grounded in inputs)```

```Style polish (witty/formal/persuasive/etc.)```

```Length normalization (short/medium/long)```

```Simulated A/B test converts a heuristic quality score to a click probability and runs a two-proportion z-test.```

```Send results as email report. Generate APP password here (https://myaccount.google.com/apppasswords)```

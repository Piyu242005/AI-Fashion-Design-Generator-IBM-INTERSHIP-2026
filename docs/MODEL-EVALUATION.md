# AI Model Evaluation

The project supports four image-generation models. Evaluation should be based on the same prompt set and measured consistently rather than relying only on visual preference.

## Benchmark protocol

Use at least 20 representative fashion prompts covering:

- casual wear
- formal wear
- ethnic wear
- streetwear
- menswear
- womenswear
- fabric-specific designs
- color-specific designs
- complex garment details
- sustainability-oriented designs

For each prompt, record the following:

| Metric | Method |
|---|---|
| Prompt adherence | Human score, 1–5 |
| Fashion detail | Human score, 1–5 |
| Visual quality | Human score, 1–5 |
| Generation latency | Seconds from request to response |
| Failure rate | Failed generations / total generations |
| Provider/model | Exact model identifier |

## Recommended score

`quality_score = 0.4 × prompt_adherence + 0.3 × fashion_detail + 0.3 × visual_quality`

Report the mean score and standard deviation for every model. Keep latency and failure rate separate so a high-quality but slow model is not incorrectly treated as the best overall option.

## Reproducibility

Keep the following fixed during a benchmark run:

- prompt set
- model parameters
- image dimensions
- evaluation rubric
- evaluator instructions
- date/time window

Do not claim benchmark results in the README until measurements have actually been collected.

## Production decision rule

Choose the default model using a weighted decision that reflects the product goal:

- quality: 50%
- prompt adherence: 25%
- latency: 15%
- failure rate: 10%

Re-run the benchmark after changing providers, models, prompts, or generation parameters.

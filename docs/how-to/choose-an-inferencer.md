# Choose an Inferencer

This guide helps you choose the right inferencer for your workload.

## Recommended Default

Start with `AutoInferencer(backend="hybrid")`.
It gives you one stable entry point and delegates to `HybridInferencer`, which uses Magic for all files and Magika only when text detection benefits from it.

```python
from filetype_detector.auto_inferencer import AutoInferencer

inferencer = AutoInferencer(backend="hybrid")
extension = inferencer.infer("document.pdf")
```

## Quick Decision Guide

| Goal | Best choice | Why |
|------|-------------|-----|
| Fastest possible detection | `LexicalInferencer` | Reads the extension from the path and does no file I/O |
| Reliable content-based detection | `MagicInferencer` | Uses libmagic and works well for binary formats |
| Highest precision for text files | `MagikaInferencer` | Uses a trained model and can return confidence scores |
| Good default for mixed workloads | `HybridInferencer` or `AutoInferencer(backend="hybrid")` | Balances speed and specificity |
| One public entry point | `AutoInferencer` | Keeps backend selection behind one interface |

## When to Use Each Inferencer

## `LexicalInferencer`

Use it when file extensions are already trustworthy and performance matters more than correction.

```python
from filetype_detector.lexical_inferencer import LexicalInferencer

inferencer = LexicalInferencer()
extension = inferencer.infer("report.pdf")
```

## `MagicInferencer`

Use it when file content matters and you want a lightweight, rule-based detector.

```python
from filetype_detector.magic_inferencer import MagicInferencer

inferencer = MagicInferencer()
extension = inferencer.infer("file_without_ext")
```

## `MagikaInferencer`

Use it when you need finer distinctions between text-based formats or confidence scores.

```python
from filetype_detector.magika_inferencer import MagikaInferencer

inferencer = MagikaInferencer()
extension, score = inferencer.infer_with_score("data.json")
```

## `HybridInferencer`

Use it when your workload mixes binary and text files and you want one strong default.

```python
from filetype_detector.hybrid_inferencer import HybridInferencer

inferencer = HybridInferencer()
extension = inferencer.infer("script.py")
```

## Rule of Thumb

Use `lexical` for trust, `magic` for validation, `magika` for text precision, and `hybrid` for mixed real-world input.

See [Inference Strategies](../explanation/inference-strategies.md) if you want the design rationale behind these trade-offs.
# AutoInferencer

Unified interface for selecting an inferencer backend with a single class.

```python
from filetype_detector.auto_inferencer import AutoInferencer, BackendType
```

## Overview

`AutoInferencer` wraps the available inferencer implementations behind one constructor.
Instead of importing a different class for each strategy, you choose a backend with the
`backend` argument.

Available backends:

- `"lexical"`: Uses `LexicalInferencer`
- `"magic"`: Uses `MagicInferencer`
- `"magika"`: Uses `MagikaInferencer`
- `"hybrid"`: Uses `HybridInferencer`

## Type Definition

```python
BackendType = Literal["lexical", "magic", "magika", "hybrid"]
```

## Basic Usage

```python
from filetype_detector.auto_inferencer import AutoInferencer

inferencer = AutoInferencer(backend="magic")
extension = inferencer.infer("file_without_ext")
```

## Backend Selection

### `backend="lexical"`

Fastest option. Extracts the extension from the path without reading file content.

```python
inferencer = AutoInferencer(backend="lexical")
extension = inferencer.infer("document.pdf")  # Returns: '.pdf'
```

### `backend="magic"`

Uses libmagic through `python-magic` to infer the type from file content.

```python
inferencer = AutoInferencer(backend="magic")
extension = inferencer.infer("file.dat")
```

### `backend="magika"`

Uses Google's Magika model for content-based detection.

```python
inferencer = AutoInferencer(backend="magika")
extension = inferencer.infer("script.py")
```

`AutoInferencer` returns only the extension. If you also need confidence scores,
use `MagikaInferencer` directly.

### `backend="hybrid"`

Uses `HybridInferencer`, which runs Magic first and applies Magika only to text files.

```python
inferencer = AutoInferencer(backend="hybrid")
extension = inferencer.infer("document.pdf")
```

This is the recommended default when you want a good balance between performance and accuracy.

## Example: Configuration-Based Selection

```python
from filetype_detector.auto_inferencer import AutoInferencer, BackendType

def detect(file_path: str, backend: BackendType = "hybrid") -> str:
    inferencer = AutoInferencer(backend=backend)
    return inferencer.infer(file_path)
```

## Example: Routing by File Type

```python
from pathlib import Path
from typing import Callable

from filetype_detector.auto_inferencer import AutoInferencer, BackendType


class FileRouter:
    def __init__(self, backend: BackendType = "magic"):
        self.inferencer = AutoInferencer(backend=backend)
        self.handlers: dict[str, Callable] = {}

    def register(self, extension: str, handler: Callable) -> None:
        self.handlers[extension] = handler

    def route(self, file_path: Path):
        extension = self.inferencer.infer(file_path)
        handler = self.handlers.get(extension)

        if handler:
            return handler(file_path)
        return None
```

## Exceptions

`AutoInferencer.infer()` forwards the behavior of the selected backend.

- `backend="lexical"`: Returns an empty string when the path has no extension
- `backend="magic"`, `"magika"`, `"hybrid"`: May raise `FileNotFoundError`, `ValueError`, or `RuntimeError`

## When to Use Direct Inferencer Classes

Use `AutoInferencer` when you want one entry point and type-safe backend selection.
Use the concrete inferencer classes directly when you need backend-specific behavior,
such as `MagikaInferencer.infer_with_score()`.

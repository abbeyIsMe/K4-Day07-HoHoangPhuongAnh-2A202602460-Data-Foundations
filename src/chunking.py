from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        stripped = text.strip()
        if not stripped:
            return []

        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", stripped) if part.strip()]
        if not sentences:
            return []

        chunks: list[str] = []
        current: list[str] = []
        for sentence in sentences:
            current.append(sentence)
            if len(current) >= self.max_sentences_per_chunk:
                chunks.append(" ".join(current).strip())
                current = []

        if current:
            chunks.append(" ".join(current).strip())

        return [chunk for chunk in chunks if chunk]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        cleaned = text.strip()
        return self._split(cleaned, self.separators[:])

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text or not current_text.strip():
            return []

        current_text = current_text.strip()
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        separator = remaining_separators[0]
        if separator == "":
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        parts = current_text.split(separator)
        if len(parts) == 1:
            return self._split(current_text, remaining_separators[1:])

        chunks: list[str] = []
        buffer = ""

        for part in parts:
            candidate = f"{buffer}{separator}{part}".strip() if buffer else part.strip()
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer)
                buffer = ""

            if len(part.strip()) <= self.chunk_size:
                buffer = part.strip()
            else:
                chunks.extend(self._split(part.strip(), remaining_separators[1:]))

        if buffer:
            chunks.append(buffer)

        final_chunks: list[str] = []
        for chunk in chunks:
            if not chunk:
                continue
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                final_chunks.extend(self._split(chunk, remaining_separators[1:]))

        return [chunk for chunk in final_chunks if chunk]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b:
        return 0.0

    dot_product = _dot(vec_a, vec_b)
    magnitude_a = math.sqrt(sum(value * value for value in vec_a))
    magnitude_b = math.sqrt(sum(value * value for value in vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if not text:
            return {
                "fixed_size": {"count": 0, "avg_length": 0.0, "chunks": []},
                "by_sentences": {"count": 0, "avg_length": 0.0, "chunks": []},
                "recursive": {"count": 0, "avg_length": 0.0, "chunks": []},
            }

        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=max(0, chunk_size // 10)).chunk(text)
        sentence = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def summarize(chunks: list[str]) -> dict:
            avg_length = sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0.0
            return {"count": len(chunks), "avg_length": avg_length, "chunks": chunks}

        return {
            "fixed_size": summarize(fixed),
            "by_sentences": summarize(sentence),
            "recursive": summarize(recursive),
        }

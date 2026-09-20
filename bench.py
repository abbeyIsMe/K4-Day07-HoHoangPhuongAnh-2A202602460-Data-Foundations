"""
Simple benchmark runner for Lab 7 R2 dataset.

Usage: python bench.py

Produces ket_qua_benchmark.txt in repo root and prints summary to stdout.
"""
from __future__ import annotations

import csv
import os
import textwrap

from src.chunking import RecursiveChunker
from src.store import EmbeddingStore
from src.models import Document

ROOT = os.path.dirname(__file__)
SOURCES_CSV = os.path.join(ROOT, "data", "ecommerce", "sources.csv")
OUT_FILE = os.path.join(ROOT, "ket_qua_benchmark.txt")

CHUNK_SIZE = 400
TOP_K = 3

# Define the five R2 benchmark queries and metadata filters
BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Người bán TikTok Shop phải xem xét yêu cầu trả hàng/hoàn tiền của người mua trong bao lâu? Nếu không xử lý đúng hạn thì điều gì xảy ra?",
        "filter": {"platform": "tiktok_shop", "audience": "seller", "category": "return_refund"},
    },
    {
        "id": 2,
        "query": "Sau khi yêu cầu trả hàng trên TikTok Shop được phê duyệt, người mua có bao nhiêu thời gian để gửi sản phẩm? Điều gì xảy ra nếu gửi trễ?",
        "filter": {"platform": "tiktok_shop", "audience": "seller", "category": "return_refund"},
    },
    {
        "id": 3,
        "query": "Trên TikTok Shop, hoàn tiền toàn bộ khác hoàn tiền một phần ở điểm nào đối với khả năng người mua gửi yêu cầu hậu mãi tiếp theo?",
        "filter": {"platform": "tiktok_shop", "audience": "seller", "category": "return_refund"},
    },
    {
        "id": 4,
        "query": "Người bán trên Shopee có trách nhiệm gì về bảo hành, và người mua cần đáp ứng những điều kiện cơ bản nào để được bảo hành?",
        "filter": {"platform": "shopee", "audience": "both", "category": "warranty"},
    },
    {
        "id": 5,
        "query": "Khi người mua gửi yêu cầu trả hàng/hoàn tiền trên Shopee, yêu cầu thường được xử lý trong bao lâu và tiền được hoàn trong bao lâu nếu yêu cầu được chấp nhận?",
        "filter": {"platform": "shopee", "audience": "buyer", "category": "return_refund"},
    },
]


def load_sources(csv_path: str) -> list[dict]:
    rows = []
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"sources.csv not found at {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main() -> None:
    rows = load_sources(SOURCES_CSV)
    chunker = RecursiveChunker(chunk_size=CHUNK_SIZE)

    # Build chunk documents
    chunks: list[Document] = []
    for row in rows:
        file_path = os.path.join(ROOT, row["file_path"]) if not os.path.isabs(row["file_path"]) else row["file_path"]
        content = read_file(file_path)
        doc_id = row.get("doc_id") or os.path.splitext(os.path.basename(file_path))[0]
        metadata = {
            "doc_id": doc_id,
            "platform": row.get("platform"),
            "audience": row.get("audience"),
            "category": row.get("category"),
            "source_url": row.get("source_url"),
        }
        if not content:
            continue
        parts = chunker.chunk(content)
        for i, part in enumerate(parts, start=1):
            chunk_id = f"{doc_id}#chunk{i}"
            chunks.append(Document(id=chunk_id, content=part, metadata={**metadata, "chunk_index": i}))

    # Index into store (uses MockEmbedder by default)
    store = EmbeddingStore()
    store.add_documents(chunks)

    # Run benchmark queries
    lines = []
    header = [f"Benchmark run: indexed_chunks={store.get_collection_size()}, chunk_size={CHUNK_SIZE}, top_k={TOP_K}"]
    lines.extend(header)
    lines.append("")

    for q in BENCHMARK_QUERIES:
        qid = q["id"]
        query = q["query"]
        metadata_filter = q.get("filter")
        results = store.search_with_filter(query, top_k=TOP_K, metadata_filter=metadata_filter)

        lines.append(f"Query {qid}: {query}")
        lines.append(f"Metadata filter: {metadata_filter}")
        if not results:
            lines.append("  No results after filter.")
            lines.append("")
            continue

        for rank, r in enumerate(results, start=1):
            excerpt = textwrap.shorten(r["content"].replace("\n", " "), width=200)
            lines.append(
                f"  Top{rank}: id={r['metadata'].get('doc_id')} (chunk_id={r['id']}) score={r['score']:.4f} excerpt={excerpt}"
            )
        lines.append("")

    # Save output
    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("Wrote:", OUT_FILE)
    print("Summary:")
    print("\n".join(lines[:10]))


if __name__ == "__main__":
    main()

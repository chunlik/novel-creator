#!/usr/bin/env python3
"""vector_search.py - 語義檢索跨章節相關內容

Usage:
  python _腳本/vector_search.py --novel 無限直播間 --query "規則陷阱" --k 5

支援 sentence-transformers（純本地，推薦多語言模型）
"""

import argparse
import json
import re
import numpy as np
from pathlib import Path

from 小說設定 import resolve_novel_folder

DEFAULT_VAULT = Path(__file__).resolve().parent.parent
INDEX_DIR_NAME = ".vector_index"


def get_chunks(vault: Path, novel: str, chunk_size: int = 500) -> list[dict]:
    chapters_dir = vault / novel / "03-章節"
    chunks = []
    if not chapters_dir.exists():
        return chunks

    for f in sorted(chapters_dir.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        body_m = re.search(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
        body = body_m.group(1).strip() if body_m else text.strip()
        if not body:
            continue

        words = list(body)
        for i in range(0, len(words), chunk_size // 2):
            segment = "".join(words[i:i + chunk_size])
            if len(segment) < 50:
                continue
            chunks.append({
                "source": f.stem,
                "text": segment,
                "start_char": i,
            })
    return chunks


def build_or_load_index(vault: Path, novel: str, chunks: list[dict]):
    index_dir = vault / INDEX_DIR_NAME
    index_dir.mkdir(parents=True, exist_ok=True)
    index_file = index_dir / f"{novel}_embeddings.npy"
    meta_file = index_dir / f"{novel}_meta.json"

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("請安裝: pip install sentence-transformers")
        raise

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    if index_file.exists() and meta_file.exists():
        embeddings = np.load(str(index_file))
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        if len(meta) == len(chunks):
            return embeddings, meta, model

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)
    np.save(str(index_file), embeddings)
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    return embeddings, chunks, model


def search(vault: Path, novel: str, query: str, k: int = 5):
    chunks = get_chunks(vault, novel)
    if not chunks:
        print("（無章節可供檢索）")
        return

    embeddings, meta, model = build_or_load_index(vault, novel, chunks)
    query_emb = model.encode([query])[0]
    scores = np.dot(embeddings, query_emb) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_emb)
    )
    top_indices = np.argsort(scores)[-k:][::-1]

    for idx in top_indices:
        score = scores[idx]
        item = meta[idx]
        print(f"\n[{item['source']}] (相關度: {score:.3f})")
        print(f"{item['text'][:300]}...")
        print("---")


def main():
    parser = argparse.ArgumentParser(description="語義檢索跨章節內容")
    parser.add_argument("--novel", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--rebuild", action="store_true", help="強制重建索引")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    args = parser.parse_args()

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    if args.rebuild:
        index_dir = vault / INDEX_DIR_NAME
        for f in index_dir.glob(f"{novel_folder}_*"):
            f.unlink()
        print("索引已清除，將重建。")
    search(vault, novel_folder, args.query, args.k)


if __name__ == "__main__":
    main()

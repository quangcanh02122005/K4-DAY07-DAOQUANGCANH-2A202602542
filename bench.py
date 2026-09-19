from __future__ import annotations

import argparse
import re
from pathlib import Path

from src import (
    ChunkingStrategyComparator,
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
)


DATA_DIR = Path("data/thu-vien")
CHUNKING_STRATEGY = "heading"
CHUNK_SIZE = 500
TOP_K = 3

QUERIES = [
    {
        "query": "Theo HUST, đến nhận phòng học nhóm muộn quá bao lâu thì lịch đặt phòng bị hủy?",
        "gold_doc_id": "dich-vu-su-dung-phong-hop-nhom",
        "gold_answer": "Nếu đến muộn quá 15 phút, thư viện có quyền hủy lịch và cấp phòng cho nhóm khác.",
        "answer_marker": "quá 15 phút",
        "metadata_filter": None,
    },
    {
        "query": "Khi mượn tài liệu đọc tại chỗ ở HUST, mỗi lần được lấy tối đa bao nhiêu quyển và phải trả ở đâu, lúc nào?",
        "gold_doc_id": "muon-tra-tai-lieu-inhouse",
        "gold_answer": "Mỗi lần lấy tối đa 2 quyển; tài liệu phải được trả trước 17h30 tại phòng 411.",
        "answer_marker": "tối đa 2 quyển",
        "metadata_filter": None,
    },
    {
        "query": "Ảnh làm thẻ thư viện cho cán bộ HUST phải đáp ứng yêu cầu gì?",
        "gold_doc_id": "quy-trinh-lam-the-can-bo",
        "gold_answer": "Ảnh tối thiểu 300 pixel, tỷ lệ 1x1, nền trắng và được gửi tới email tttts@hust.edu.vn.",
        "answer_marker": "300 Pixel",
        "metadata_filter": {"audience": "faculty"},
    },
    {
        "query": "Theo HaUI, sinh viên được mượn tối đa bao nhiêu tài liệu và trong thời gian bao lâu?",
        "gold_doc_id": "haui-library-policy",
        "gold_answer": "Mỗi lần được mượn tối đa 5 tài liệu; tài liệu tham khảo tối đa 15 ngày và giáo trình tối đa một học kỳ.",
        "answer_marker": "tối đa 15 ngày",
        "metadata_filter": None,
    },
    {
        "query": "Tôi cần làm gì để hoàn tất thủ tục công nợ tại thư viện?",
        "gold_doc_id": "thu-tuc-thanh-toan-ra-truong",
        "gold_answer": "Kiểm tra tài khoản hoặc email, trả sách và xử lý vi phạm, kiểm tra lại tài khoản rồi đề nghị cán bộ phòng mượn khóa tài khoản.",
        "answer_marker": "khóa tài khoản",
        "metadata_filter": {"audience": "student"},
    },
]


class HeadingChunker:
    """Split library rules at Markdown headings and numbered procedural sections."""

    HEADING = re.compile(r"^(?:#{1,6}\s+|Chương\s+|Điều\s+|\d+\.\s+|Bước\s+\d+[:.]?)", re.I)

    def __init__(self, chunk_size: int = CHUNK_SIZE) -> None:
        self.chunk_size = chunk_size
        self.fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        sections: list[tuple[str, str]] = []
        heading = ""
        content: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if self.HEADING.match(stripped):
                if heading or content:
                    sections.append((heading, "\n".join(content).strip()))
                heading, content = stripped, []
            elif stripped:
                content.append(stripped)
        if heading or content:
            sections.append((heading, "\n".join(content).strip()))

        chunks: list[str] = []
        for section_heading, section_content in sections:
            section = "\n".join(part for part in (section_heading, section_content) if part)
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            for piece in self.fallback.chunk(section_content or section_heading):
                if section_heading and not piece.startswith(section_heading):
                    piece = f"{section_heading}\n{piece}"
                chunks.append(piece)
        return [chunk for chunk in chunks if chunk.strip()]


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not match:
        raise ValueError(f"Missing front matter: {path}")
    metadata = {
        key: value.strip().strip('"')
        for key, value in re.findall(r"^(\w+):\s*(.+)$", match.group(1), re.M)
    }
    return metadata, match.group(2).strip()


def make_chunker(strategy: str = CHUNKING_STRATEGY):
    strategies = {
        "fixed_size": FixedSizeChunker(chunk_size=CHUNK_SIZE, overlap=50),
        "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
        "recursive": RecursiveChunker(chunk_size=CHUNK_SIZE),
        "heading": HeadingChunker(chunk_size=CHUNK_SIZE),
    }
    return strategies[strategy]


def load_chunks(strategy: str = CHUNKING_STRATEGY) -> list[Document]:
    chunker = make_chunker(strategy)
    documents: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, content = read_markdown(path)
        for index, chunk in enumerate(chunker.chunk(content)):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={**metadata, "doc_id": path.stem, "chunk_index": index},
                )
            )
    return documents


def print_baseline() -> None:
    print("=== BASELINE CHUNKING (front matter excluded) ===")
    baseline_files = [
        "haui-library-policy.md",
        "huit-library-usage-policy.md",
        "thu-tuc-thanh-toan-ra-truong.md",
    ]
    comparator = ChunkingStrategyComparator()
    for filename in baseline_files:
        _, content = read_markdown(DATA_DIR / filename)
        for strategy, stats in comparator.compare(content, chunk_size=CHUNK_SIZE).items():
            print(
                f"{filename:38} {strategy:14} "
                f"count={stats['count']:3} avg_length={stats['avg_length']:.1f}"
            )


def print_results(store: EmbeddingStore, strategy: str) -> int:
    print(f"\n=== BENCHMARK: strategy={strategy}, top_k={TOP_K} ===")
    total_score = 0
    for number, item in enumerate(QUERIES, start=1):
        results = store.search_with_filter(
            item["query"], top_k=TOP_K, metadata_filter=item["metadata_filter"]
        )
        print(f"\nQ{number}: {item['query']}")
        print(f"FILTER: {item['metadata_filter']}")
        print(f"GOLD: {item['gold_answer']}")
        answer_rank = 0
        for rank, result in enumerate(results, start=1):
            contains_answer = item["answer_marker"].casefold() in result["content"].casefold()
            if contains_answer and not answer_rank:
                answer_rank = rank
            preview = " ".join(result["content"].split())[:180]
            print(
                f"  {rank}. score={result['score']:.4f} "
                f"doc_id={result['metadata'].get('doc_id')} "
                f"answer={'YES' if contains_answer else 'NO'} | {preview}"
            )
        points = 2 if answer_rank == 1 else 1 if answer_rank in {2, 3} else 0
        total_score += points
        print(f"TOP3_CONTAINS_ANSWER: {'YES' if answer_rank else 'NO'}")
        print(f"QUESTION_SCORE: {points}/2")

        if item["metadata_filter"] == {"audience": "student"}:
            unfiltered = store.search(item["query"], top_k=TOP_K)
            print("  A/B WITHOUT FILTER:")
            for rank, result in enumerate(unfiltered, start=1):
                print(
                    f"    {rank}. score={result['score']:.4f} "
                    f"doc_id={result['metadata'].get('doc_id')} "
                    f"audience={result['metadata'].get('audience')}"
                )
    print(f"\nBENCHMARK_SCORE: {total_score}/10")
    return total_score


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the library retrieval benchmark.")
    parser.add_argument(
        "--strategy",
        choices=["fixed_size", "by_sentences", "recursive", "heading"],
        default=CHUNKING_STRATEGY,
    )
    args = parser.parse_args()
    print_baseline()
    chunks = load_chunks(args.strategy)
    store = EmbeddingStore(collection_name="library_benchmark")
    store.add_documents(chunks)
    print(f"\nLoaded {len(chunks)} chunks from {len(list(DATA_DIR.glob('*.md')))} documents")
    print_results(store, args.strategy)
    print("\nNOTE: MockEmbedder is deterministic but has no semantic meaning; retrieval scores are illustrative only.")


if __name__ == "__main__":
    main()

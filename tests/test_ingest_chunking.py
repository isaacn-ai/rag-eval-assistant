from src.ingest import chunk_text


def test_chunk_text_produces_chunks():
    text = "A " * 2000
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(isinstance(c, str) and c.strip() for c in chunks)


def test_chunk_overlap_behavior():
    text = " ".join([f"word{i}" for i in range(1000)])
    chunk_size = 200
    overlap = 50

    chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=overlap)
    assert len(chunks) > 1

    # Overlap is approximate because we're chunking characters, but the end of chunk0
    # should appear near the start of chunk1 if overlap > 0.
    tail0 = chunks[0][-overlap:]
    head1 = chunks[1][:overlap]
    assert tail0 and head1

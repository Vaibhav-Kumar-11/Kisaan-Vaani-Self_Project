from retrieval import DocumentRetriever


def test_retriever_finds_best_match():
    docs = [
        {"id": "a", "text": "apple banana orange"},
        {"id": "b", "text": "wheat rice sugarcane"},
    ]
    retriever = DocumentRetriever(docs, lambda d: d["text"])

    results = retriever.search("banana smoothie recipe", top_k=1)

    assert results[0]["id"] == "a"


def test_retriever_empty_query_returns_nothing():
    docs = [{"id": "a", "text": "apple"}]
    retriever = DocumentRetriever(docs, lambda d: d["text"])
    assert retriever.search("", top_k=1) == []


def test_retriever_no_documents():
    retriever = DocumentRetriever([], lambda d: d["text"])
    assert retriever.search("anything") == []

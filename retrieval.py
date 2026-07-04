"""Lightweight lexical retrieval over the small, fixed knowledge base used
by the schemes and advisory modules.

TF-IDF + cosine similarity, not embeddings — deliberately. The knowledge
base is a handful of short, keyword-heavy documents (scheme names, crop
names), so lexical similarity retrieves well without pulling in a large
embedding model. That matters on a free-tier Streamlit Cloud deploy, where
a torch/sentence-transformers install risks slow cold starts or hitting
memory limits. If this knowledge base grew to hundreds of long-form docs,
semantic embeddings would be the right next step — noted as such rather
than built preemptively.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DocumentRetriever:
    def __init__(self, documents: list[dict], text_fn):
        """
        documents : raw doc dicts (e.g. one per scheme or crop)
        text_fn   : function(doc) -> str, the text TF-IDF searches over
        """
        self.documents = documents
        self._vectorizer = None
        self._matrix = None

        if documents:
            texts = [text_fn(doc) for doc in documents]
            self._vectorizer = TfidfVectorizer(stop_words="english")
            self._matrix = self._vectorizer.fit_transform(texts)

    def search(self, query: str, top_k: int = 1) -> list[dict]:
        if not self.documents or not query.strip():
            return []
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(range(len(self.documents)), key=lambda i: scores[i], reverse=True)
        return [self.documents[i] for i in ranked[:top_k]]

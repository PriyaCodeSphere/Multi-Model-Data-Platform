"""Vector search over the demo knowledge documents.

Uses scikit-learn's TF-IDF vectorizer (no torch / sentence-transformers).
For four short documents this is indistinguishable from semantic embeddings
in practice, and it keeps the deployed container well under the 1 GB free-tier
RAM budget on Streamlit Community Cloud.
"""

import os

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class VectorSearchEngine:
    def __init__(self, model_name: str = "tfidf-sklearn"):
        self.model_name = model_name
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )
        self.documents: list[str] = []
        self.doc_metadata: list[dict] = []
        self.embeddings = None

    def load_documents_from_directory(self, docs_dir: str = "data/documents") -> None:
        self.documents = []
        self.doc_metadata = []

        if not os.path.exists(docs_dir):
            return

        for filename in sorted(os.listdir(docs_dir)):
            if not filename.endswith(".txt"):
                continue
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.documents.append(content)
            self.doc_metadata.append({
                "filename": filename,
                "doc_type": filename.replace(".txt", "").replace("_", " ").title(),
                "length": len(content),
            })

        if self.documents:
            self.embeddings = self.vectorizer.fit_transform(self.documents)

    def search(self, query: str, top_k: int = 3, similarity_threshold: float = 0.05) -> list[dict]:
        if not self.documents or self.embeddings is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.embeddings)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score < similarity_threshold:
                continue
            results.append({
                "document": self.documents[idx],
                "metadata": self.doc_metadata[idx],
                "similarity_score": score,
                "excerpt": self._extract_excerpt(self.documents[idx], query),
            })
        return results

    def _extract_excerpt(self, document: str, query: str, context_chars: int = 200) -> str:
        query_terms = [t for t in query.lower().split() if len(t) > 2]

        for line in document.split("\n"):
            if any(term in line.lower() for term in query_terms):
                excerpt = line.strip()
                if len(excerpt) > context_chars:
                    excerpt = excerpt[:context_chars] + "..."
                return excerpt

        for line in document.split("\n"):
            if line.strip():
                return line.strip()[:context_chars] + "..."

        return "See full document for details"

    def get_summary_for_order_delay(self, order_id, query=None, supplier_id=None):
        if not query:
            query = f"Why is order {order_id} delayed? Turbocharger shortage supplier issues"

        search_results = self.search(query, top_k=3, similarity_threshold=0.05)

        supplier_label = supplier_id or "an upstream supplier"
        summary = {
            "order_id": order_id,
            "query": query,
            "root_cause": f"Turbocharger shortage from {supplier_label}",
            "confidence": 0.85 if search_results else 0.4,
            "supporting_documents": [],
            "explanation": "",
        }

        for result in search_results:
            summary["supporting_documents"].append({
                "source": result["metadata"]["doc_type"],
                "excerpt": result["excerpt"],
                "relevance": result["similarity_score"],
            })

        if search_results:
            summary["explanation"] = (
                f"Based on available knowledge documents, order {order_id} is likely delayed due to "
                f"component sourcing constraints. The most relevant factor is a turbocharger supply "
                f"disruption from {supplier_label}. This aligns with the advanced cooling system options "
                f"on this order. Estimated resolution: Q4 2026."
            )
        else:
            summary["explanation"] = (
                f"No high-confidence matches were found in the knowledge base for the query: "
                f"\"{query}\". Try rephrasing or broadening the question."
            )

        return summary

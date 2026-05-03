"""
Simple QnA Indexing System (Beginner Version)
---------------------------------------------
This script:
- Loads Q&A data from CSV
- Cleans text
- Creates TF-IDF embeddings
- Stores vectors in FAISS index
- Retrieves similar answers using search
"""

import pandas as pd
import numpy as np
import re
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer


# =========================
# 1. TEXT CLEANING
# =========================

def clean_text(text):
    """Remove special characters and make text lowercase."""
    if isinstance(text, str):
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        text = text.lower().strip()
        return text
    return ""


# =========================
# 2. LOAD DATASET
# =========================

def load_data(file_path):
    """Load CSV file and remove empty rows."""
    df = pd.read_csv(file_path)
    df = df.dropna()

    df = df[df["Question"].astype(str).str.strip() != ""]
    df = df[df["Answer"].astype(str).str.strip() != ""]

    print("Dataset loaded:", len(df), "rows")
    return df


# =========================
# 3. CREATE EMBEDDINGS
# =========================

def create_embeddings(questions):
    """Convert text into TF-IDF vectors."""
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=800,
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(questions).toarray()

    print("Embeddings shape:", vectors.shape)
    return vectorizer, vectors


# =========================
# 4. BUILD FAISS INDEX
# =========================

def build_index(vectors):
    """Create FAISS index for similarity search."""
    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(vectors.astype("float32"))

    return index


# =========================
# 5. SEARCH FUNCTION
# =========================

def search_answer(query, vectorizer, index, df, top_k=3):
    """Find most similar Q&A pairs."""

    query = clean_text(query)
    query_vector = vectorizer.transform([query]).toarray().astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for i in range(len(indices[0])):
        idx = indices[0][i]

        if idx < len(df):
            results.append({
                "question": df.iloc[idx]["Question"],
                "answer": df.iloc[idx]["Answer"],
                "score": float(distances[0][i])
            })

    return results


# =========================
# 6. MAIN PROGRAM
# =========================

if __name__ == "__main__":

    # Load data
    data_file = "university_qa.csv"
    df = load_data(data_file)

    # Clean questions
    questions = [clean_text(q) for q in df["Question"]]

    # Create embeddings
    vectorizer, vectors = create_embeddings(questions)

    # Build FAISS index
    index = build_index(vectors)

    # Test system
    print("\n--- Testing QnA System ---")

    test_queries = [
        "What programs are available?",
        "When is admission deadline?",
        "Fee structure?"
    ]

    for q in test_queries:
        print("\nQuery:", q)

        results = search_answer(q, vectorizer, index, df)

        for r in results:
            print("Q:", r["question"])
            print("A:", r["answer"])
            print("Score:", round(r["score"], 4))

    print("\nSystem Ready!")
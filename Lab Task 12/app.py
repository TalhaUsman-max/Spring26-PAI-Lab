"""
Smart University Assistant API
Advanced Flask + FAISS Semantic Retrieval System
------------------------------------------------
This application provides intelligent university-related
question answering using TF-IDF embeddings and FAISS
vector similarity search.
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path

import pandas as pd
import numpy as np
import faiss
import re

from sklearn.feature_extraction.text import TfidfVectorizer


# =========================================================
# Flask App Configuration
# =========================================================

web_app = Flask(__name__)

# =========================================================
# File Paths
# =========================================================

DATASET_PATH = Path("university_qa.csv")
VECTOR_INDEX_PATH = Path("qa_faiss.index")


# =========================================================
# Semantic Engine Class
# =========================================================

class UniversitySemanticEngine:
    """
    Handles:
    - Dataset loading
    - Text preprocessing
    - Vector generation
    - FAISS similarity retrieval
    """

    def __init__(self):
        self.embedding_model = None
        self.semantic_index = None
        self.knowledge_base = None

    # -----------------------------------------------------
    # Text Sanitization
    # -----------------------------------------------------

    @staticmethod
    def normalize_sentence(raw_text: str) -> str:
        """
        Cleans and standardizes text input.
        """
        if not isinstance(raw_text, str):
            return ""

        purified_text = re.sub(r"[^a-zA-Z\s]", " ", raw_text)
        purified_text = re.sub(r"\s+", " ", purified_text)

        return purified_text.lower().strip()

    # -----------------------------------------------------
    # Initialization Pipeline
    # -----------------------------------------------------

    def boot_engine(self) -> None:
        """
        Loads dataset, prepares embeddings,
        and restores FAISS vector index.
        """

        if not DATASET_PATH.exists():
            raise FileNotFoundError(
                f"Dataset not found -> {DATASET_PATH}"
            )

        if not VECTOR_INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found -> {VECTOR_INDEX_PATH}"
            )

        # Load CSV Knowledge Base
        dataset_frame = pd.read_csv(DATASET_PATH)
        dataset_frame.dropna(inplace=True)

        self.knowledge_base = dataset_frame

        # Prepare Questions
        processed_questions = (
            dataset_frame["Question"]
            .astype(str)
            .apply(self.normalize_sentence)
            .tolist()
        )

        # TF-IDF Embedding Generator
        self.embedding_model = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=1000,
            stop_words="english",
            sublinear_tf=True
        )

        self.embedding_model.fit(processed_questions)

        # Load FAISS Vector Store
        self.semantic_index = faiss.read_index(
            str(VECTOR_INDEX_PATH)
        )

        print("Semantic Retrieval Engine Activated Successfully")

    # -----------------------------------------------------
    # Similarity Retrieval
    # -----------------------------------------------------

    def fetch_best_response(
        self,
        user_query: str,
        top_k: int = 1
    ) -> str:
        """
        Finds the most semantically similar answer.
        """

        if not user_query.strip():
            return "Please enter a valid question."

        # Clean Query
        refined_query = self.normalize_sentence(user_query)

        # Convert into Vector Representation
        query_vector = (
            self.embedding_model
            .transform([refined_query])
            .toarray()
            .astype("float32")
        )

        # Similarity Search
        similarity_scores, matched_ids = (
            self.semantic_index.search(
                query_vector,
                top_k
            )
        )

        # Validate Result
        if matched_ids.size == 0:
            return (
                "No relevant information was found "
                "for your query."
            )

        top_match_index = int(matched_ids[0][0])

        if top_match_index >= len(self.knowledge_base):
            return (
                "Retrieved result exceeds dataset bounds."
            )

        # Extract Answer
        intelligent_reply = (
            self.knowledge_base.iloc[top_match_index]["Answer"]
        )

        return intelligent_reply


# =========================================================
# Initialize AI Engine
# =========================================================

semantic_assistant = UniversitySemanticEngine()
semantic_assistant.boot_engine()


# =========================================================
# Flask Routes
# =========================================================

@web_app.route("/")
def landing_page():
    """
    Render homepage UI.
    """
    return render_template("index.html")


@web_app.route("/chat", methods=["POST"])
def conversational_gateway():
    """
    Handles chatbot communication.
    """

    incoming_message = request.form.get("msg", "").strip()

    generated_response = (
        semantic_assistant.fetch_best_response(
            incoming_message
        )
    )

    api_payload = {
        "question": incoming_message,
        "response": generated_response,
        "status": "success"
    }

    return jsonify(api_payload)


# =========================================================
# Application Entry Point
# =========================================================

if __name__ == "__main__":

    web_app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
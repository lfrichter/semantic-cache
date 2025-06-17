# Semantic Cache

[![semantic-cache](https://img.shields.io/github/stars/lfrichter/semantic-cache?style=flat&logo=github)](https://github.com/lfrichter/semantic-cache)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Ollama Compatible](https://img.shields.io/badge/Ollama-Compatible-green?logo=Ollama)](https://ollama.com/)
[![FAISS Version](https://img.shields.io/badge/FAISS-Latest-red?logo=facebook)](https://faiss.ai/)
[![Vector Search](https://img.shields.io/badge/Vector%20Search-Enabled-blueviolet?logo=elasticsearch)](https://faiss.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow?logo=open-source-initiative)](https://app.outlier.ai/playground/LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?logo=github-actions)](https://github.com/yourusername/semantic-cache)

A blazing-fast, local-first semantic cache designed to sit in front of Large Language Models. It leverages the power of local embeddings and vector search to dramatically reduce latency and computational load by reusing answers from previously seen, semantically similar questions.

## 🚀 Tech Stack & Core Concepts

This project is built on a simple yet powerful stack, running entirely on your local machine with no external dependencies or API keys required.

* **[Ollama](https://ollama.com/)**: Serves as the local inference engine for generating high-quality text embeddings. By using Ollama, this cache can leverage a wide variety of powerful open-source models (like `Mistral`, `Llama3`, `Gemma`, etc.) to understand the semantic meaning of user queries.

* **[FAISS (Facebook AI Similarity Search)](https://faiss.ai/)**: The core of our vector search engine. FAISS is an incredibly efficient library for similarity search among millions of vectors. We use it to create an in-memory index of query embeddings, allowing for near-instantaneous retrieval of the most similar past questions.

* **Python & NumPy**: The glue that holds everything together. Python provides the main application logic, while NumPy offers the robust, high-performance array objects needed to handle the vectors passed between Ollama and FAISS.

## ⚙️ How It Works

The workflow is designed for speed and efficiency:

1.  **Query Input**: The system receives a new user query.
2.  **Embedding Generation**: **Ollama** converts the text query into a dense vector embedding—a numerical representation of its meaning.
3.  **Similarity Search**: **FAISS** takes this new vector and searches its index to find the nearest neighbor (i.e., the most semantically similar query from the past).
4.  **Cache Logic**:
    * **HIT**: If the distance to the nearest neighbor is below a configurable threshold, it's a "cache hit." The system retrieves the pre-existing answer and returns it instantly.
    * **MISS**: If the distance is too great, it's a "cache miss." The query is sent to the LLM for a fresh answer. This new query embedding and its corresponding answer are then stored in FAISS and our response cache for future use.

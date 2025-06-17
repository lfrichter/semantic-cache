
-----

# 🛸 Semantic Cache



[![semantic-cache](https://img.shields.io/github/stars/lfrichter/semantic-cache?style=flat&logo=github)](https://github.com/lfrichter/semantic-cache)

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)

[![NumPy](https://img.shields.io/badge/NumPy-2.3.0-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org)

[![Ollama Compatible](https://img.shields.io/badge/Ollama-Compatible-green?logo=Ollama)](https://ollama.com/)

[![FAISS Version](https://img.shields.io/badge/FAISS-Latest-red?logo=facebook)](https://faiss.ai/)

[![Vector Search](https://img.shields.io/badge/Vector%20Search-Enabled-blueviolet?logo=elasticsearch)](https://faiss.ai/)

[![License](https://img.shields.io/badge/License-MIT-yellow?logo=open-source-initiative)](https://app.outlier.ai/playground/LICENSE)

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?logo=github-actions)](https://github.com/yourusername/semantic-cache)

A blazing-fast, *local-first* semantic cache designed to sit in front of Large Language Models (LLMs). It leverages the power of local *embeddings* and vector search to **dramatically reduce latency** and computational load by reusing answers from previously seen, semantically similar questions.

-----

## 💡 Core Concepts & Tech Stack

This project is built on a simple yet powerful stack, running entirely on your local machine with no external dependencies or API keys required.

  * **[Ollama](https://ollama.com/)**: Serves as the local inference engine for generating high-quality text embeddings. By using Ollama, this cache can leverage a wide variety of powerful *open-source* models (like `Mistral`, `Llama3`, `Gemma`, etc.) to understand the semantic meaning of user queries.

  * **[FAISS](https://faiss.ai/)** (*Facebook AI Similarity Search*): The core of our vector search engine. FAISS is an incredibly efficient library for similarity search and clustering of dense vectors. We use it to create an in-memory index of query embeddings, allowing for near-instantaneous retrieval of the most similar past questions.

  * **Python & NumPy**: The glue that holds everything together. Python provides the main application logic, while NumPy offers the robust, high-performance array objects needed to handle the vectors passed between Ollama and FAISS.

## ⚙️ How It Works

The workflow is designed for speed and efficiency:

1.  **Query Input**: The system receives a new user query.
2.  **Embedding Generation**: **Ollama** converts the text query into a dense vector *embedding*—a numerical representation of its meaning.
3.  **Similarity Search**: **FAISS** takes this new vector and searches its index to find the nearest neighbor (i.e., the most semantically similar query from the past).
4.  **Cache Logic**:
      * ***HIT***: If the distance to the nearest neighbor is below a configurable threshold (`THRESHOLD`), a *cache hit* is triggered. The system retrieves the pre-existing answer and returns it instantly.
      * ***MISS***: If the distance is too great, a *cache miss* occurs. The query is sent to the LLM for a new generation. This new query's *embedding* and its corresponding answer are then stored in FAISS and our response cache for future use.

## 📦 Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/lfrichter/semantic-cache.git
    cd semantic-cache
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: Ensure your `requirements.txt` file contains `faiss-cpu`, `ollama`, and `numpy`)*

## ▶️ Usage

1.  **Ensure Ollama is running** and that you have the required model.

    ```bash
    # Pull the model if you don't have it yet
    ollama pull mistral:7b
    ```

2.  **Run the cache script:**

    ```bash
    python semantic_cache.py
    ```


## 📋 Example Output

```bash
Semantic Cache initialized with model 'mistral:7b' and dimension 4096.

🔎 Processing query: 'What is the capital of France?'
Cache empty. Generating new response...
Generating new response with LLM...
New response generated and added to cache with ID 0.
✔️ Response (new): 'This is a new response for 'What is the capital of France?' generated at 21:46:54'

🔎 Processing query: 'What is the French capital?'
🎯 CACHE HIT! Distance: 0.0622 (< 0.2)
Retrieving response from ID: 0
✔️ Response (from cache): 'This is a new response for 'What is the capital of France?' generated at 21:46:54'
⏱️ Total time: 0.17 seconds.

🔎 Processing query: 'Who wrote Don Quixote?'
❌ CACHE MISS. Minimum distance: 0.5731 (>= 0.2)
Generating new response with LLM...
New response generated and added to cache with ID 1.
✔️ Response (new): 'This is a new response for 'Who wrote Don Quixote?' generated at 21:46:56'
⏱️ Total time: 0.13 seconds.

🔎 Processing query: 'What is the main city in France?'
❌ CACHE MISS. Minimum distance: 0.2089 (>= 0.2)
Generating new response with LLM...
New response generated and added to cache with ID 2.
✔️ Response (new): 'This is a new response for 'What is the main city in France?' generated at 21:46:58'
⏱️ Total time: 0.15 seconds.

🔎 Processing query: 'What is the color of the sky?'
❌ CACHE MISS. Minimum distance: 0.4674 (>= 0.2)
Generating new response with LLM...
New response generated and added to cache with ID 3.
✔️ Response (new): 'This is a new response for 'What is the color of the sky?' generated at 21:46:59'
⏱️ Total time: 0.16 seconds.
```


## 🧠 Analysis of Results

  * **The Obvious Hit** (Distance: `0.0473`): The query *"Qual é a capital francesa?"* is an almost direct paraphrase of *"Qual a capital da França?"*. The system recognized this with an extremely low distance, resulting in a perfect and fast *hit*.

  * **The Smart Hit** (Distance: `0.1416`): This is the most impressive result. The query *"Qual a principal cidade da França?"* is not the same, but *semantically it is very close*. The system was smart enough to understand this proximity, and since the distance was below our `THRESHOLD` of `0.2`, it served the cached answer. Notice how the distance is greater than the first hit, which is logical and expected.

  * **The Correct Misses** (Distances `0.6777` & `0.5936`): The queries about *"Dom Quixote"* and *"a cor do céu"* are semantically very distant from the "capital of France" topic. The system calculated high distances, well above the threshold, and correctly identified them as *misses*. This proves the cache is not being too "permissive".

## 🛠️ Next Steps & Improvements

  * **Fine-Tuning the `THRESHOLD`**: Experiment with the `0.2` value. A lower value (e.g., `0.15`) would make the cache stricter, while a higher value (e.g., `0.3`) would make it more lenient.
  * **Persistence**: Implement saving (`faiss.write_index`) and loading (`faiss.read_index`) of the FAISS index and the response dictionary to allow the cache to persist between runs.
  * **Real Responses**: Modify the `_cache_miss` method to actually call the LLM (`ollama.chat`) and store the real generated response.
  * **Cache Invalidation**: For a more advanced system, consider how to invalidate or update a cached response if better information becomes available.

## 📜 License

This project is distributed under the MIT License. See the `LICENSE` file for more details.

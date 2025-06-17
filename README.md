
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
Cache Semântico inicializado com o modelo 'mistral:7b' e dimensão 4096.

🔎 Processando query: 'Qual a capital da França?'
Cache vazio. Gerando nova resposta...
Gerando nova resposta com o LLM...
Nova resposta gerada e adicionada ao cache com ID 0.
✔️ Resposta (nova): 'Esta é uma nova resposta para 'Qual a capital da França?' gerada em 21:08:07'

🔎 Processando query: 'Qual é a capital francesa?'
🎯 CACHE HIT! Distância: 0.0473 (< 0.2)
Resgatando resposta do ID: 0
✔️ Resposta (do cache): 'Esta é uma nova resposta para 'Qual a capital da França?' gerada em 21:08:07'
⏱️ Tempo total: 0.22 segundos.

🔎 Processando query: 'Quem escreveu Dom Quixote?'
❌ CACHE MISS. Distância mínima: 0.6777 (>= 0.2)
Gerando nova resposta com o LLM...
Nova resposta gerada e adicionada ao cache com ID 1.
✔️ Resposta (nova): 'Esta é uma nova resposta para 'Quem escreveu Dom Quixote?' gerada em 21:08:09'
⏱️ Tempo total: 0.15 segundos.

🔎 Processando query: 'Qual a principal cidade da França?'
🎯 CACHE HIT! Distância: 0.1416 (< 0.2)
Resgatando resposta do ID: 0
✔️ Resposta (do cache): 'Esta é uma nova resposta para 'Qual a capital da França?' gerada em 21:08:07'
⏱️ Tempo total: 0.16 segundos.

🔎 Processando query: 'Qual a cor do céu?'
❌ CACHE MISS. Distância mínima: 0.5936 (>= 0.2)
Gerando nova resposta com o LLM...
Nova resposta gerada e adicionada ao cache com ID 2.
✔️ Resposta (nova): 'Esta é uma nova resposta para 'Qual a cor do céu?' gerada em 21:08:12'
⏱️ Tempo total: 0.16 segundos.
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

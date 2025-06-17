# semantic_cache.py - Internationalized Version
import faiss
import numpy as np
import ollama
import time

# --- Configurations ---
OLLAMA_MODEL = 'mistral:7b'
EMBEDDING_DIM = 4096
CACHE_THRESHOLD = 0.2

class SemanticCache:
    def __init__(self, dimension: int, model: str):
        self.model = model
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.response_cache = {}
        print(f"Semantic Cache initialized with model '{self.model}' and dimension {self.dimension}.")

    def _get_embedding(self, text: str) -> np.ndarray:
        """Generates and NORMALIZES an embedding for a given text."""
        try:
            response = ollama.embeddings(model=self.model, prompt=text)
            embedding = np.array(response['embedding']).astype('float32')

            norm = np.linalg.norm(embedding)
            if norm == 0:
                return embedding.reshape(1, -1)

            normalized_embedding = embedding / norm
            return normalized_embedding.reshape(1, -1)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def process_query(self, query: str):
        """Processes a query, checking the cache before generating a new response."""
        print(f"\n🔎 Processing query: '{query}'")
        start_time = time.time()

        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            print("Could not process your query.")
            return

        if self.index.ntotal == 0:
            print("Cache empty. Generating new response...")
            self._cache_miss(query, query_embedding)
            return

        D, I = self.index.search(query_embedding, k=1)
        distance = D[0][0]
        retrieved_id = I[0][0]

        if distance < CACHE_THRESHOLD:
            # CACHE HIT
            cached_response = self.response_cache[retrieved_id]
            print(f"🎯 CACHE HIT! Distance: {distance:.4f} (< {CACHE_THRESHOLD})")
            print(f"Retrieving response from ID: {retrieved_id}")
            print(f"✔️ Response (from cache): '{cached_response}'")
        else:
            # CACHE MISS
            print(f"❌ CACHE MISS. Minimum distance: {distance:.4f} (>= {CACHE_THRESHOLD})")
            self._cache_miss(query, query_embedding)

        end_time = time.time()
        print(f"⏱️ Total time: {end_time - start_time:.2f} seconds.")

    def _cache_miss(self, query: str, query_embedding: np.ndarray):
        """Handles a cache miss: generates a response, adds it to the index and cache."""
        print("Generating new response with LLM...")
        # In a real scenario, you would call ollama.generate() or ollama.chat() here.
        new_response = f"This is a new response for '{query}' generated at {time.strftime('%H:%M:%S')}"

        new_id = self.index.ntotal
        self.index.add(query_embedding)

        self.response_cache[new_id] = new_response

        print(f"New response generated and added to cache with ID {new_id}.")
        print(f"✔️ Response (new): '{new_response}'")


# --- Demonstration ---
if __name__ == "__main__":
    cache = SemanticCache(dimension=EMBEDDING_DIM, model=OLLAMA_MODEL)

    queries = [
        "What is the capital of France?",
        "What is the French capital?",
        "Who wrote Don Quixote?",
        "What is the main city in France?",
        "What is the color of the sky?"
    ]

    for q in queries:
        cache.process_query(q)
        time.sleep(1) # Pause for easier reading of the output

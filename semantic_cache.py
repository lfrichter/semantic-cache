import faiss
import numpy as np
import ollama
import time

# --- Configurações ---
OLLAMA_MODEL = 'mistral:7b'
# A dimensão do embedding para o 'mistral:7b' é 4096.
# Verifique a dimensão correta para outros modelos.
EMBEDDING_DIM = 4096
# Threshold de distância para considerar um "cache hit".
# Este valor é crucial e precisa de ajuste empírico.
# Distâncias menores = queries mais similares para um hit.
CACHE_THRESHOLD = 0.2
# Ajuste Fino do THRESHOLD: experimentar com o valor 0.2. Um valor menor (ex: 0.1)
# tornaria o cache mais rigoroso, enquanto um valor maior (ex: 0.3) o
# tornaria mais abrangente, com o risco de alguns falsos positivos.

class SemanticCache:
    def __init__(self, dimension: int, model: str):
        """
        Inicializa o cache semântico.

        Args:
            dimension (int): A dimensão dos vetores de embedding.
            model (str): O nome do modelo no Ollama para gerar embeddings.
        """
        self.model = model
        self.dimension = dimension
        # IndexFlatL2 calcula a distância Euclidiana (L2) ao quadrado.
        self.index = faiss.IndexFlatL2(dimension)
        # Armazena as respostas. O ID do FAISS mapeia para a resposta.
        self.response_cache = {}
        print(f"Cache Semântico inicializado com o modelo '{self.model}' e dimensão {self.dimension}.")

    def _get_embedding(self, text: str) -> np.ndarray:
        """Gera um embedding para um texto e o NORMALIZA."""
        try:
            response = ollama.embeddings(model=self.model, prompt=text)
            embedding = np.array(response['embedding']).astype('float32')

            # --- PASSO CRÍTICO DE NORMALIZAÇÃO ---
            # Calcula a norma L2 (magnitude) do vetor. Adiciona um valor pequeno (1e-9) para evitar divisão por zero.
            norm = np.linalg.norm(embedding)
            if norm == 0:
                return embedding.reshape(1, -1) # Retorna o vetor zero se a norma for zero

            # Divide cada elemento do vetor pela sua norma.
            normalized_embedding = embedding / norm
            # ------------------------------------

            return normalized_embedding.reshape(1, -1)
        except Exception as e:
            print(f"Erro ao gerar embedding: {e}")
            return None

    def process_query(self, query: str):
        """
        Processa uma query, verificando o cache antes de gerar uma nova resposta.
        """
        print(f"\n🔎 Processando query: '{query}'")
        start_time = time.time()

        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return "Não foi possível processar a sua query."

        # Se o índice estiver vazio, é um cache miss direto.
        if self.index.ntotal == 0:
            print("Cache vazio. Gerando nova resposta...")
            self._cache_miss(query, query_embedding)
            return

        # Busca no FAISS pelo vizinho mais próximo (k=1)
        # D = distância (L2 ao quadrado), I = ID do vetor
        D, I = self.index.search(query_embedding, k=1)
        distance = D[0][0]
        retrieved_id = I[0][0]

        # Lógica de Cache Hit/Miss
        if distance < CACHE_THRESHOLD:
            # CACHE HIT
            cached_response = self.response_cache[retrieved_id]
            print(f"🎯 CACHE HIT! Distância: {distance:.4f} (< {CACHE_THRESHOLD})")
            print(f"Resgatando resposta do ID: {retrieved_id}")
            print(f"✔️ Resposta (do cache): '{cached_response}'")
        else:
            # CACHE MISS
            print(f"❌ CACHE MISS. Distância mínima: {distance:.4f} (>= {CACHE_THRESHOLD})")
            self._cache_miss(query, query_embedding)

        end_time = time.time()
        print(f"⏱️ Tempo total: {end_time - start_time:.2f} segundos.")

    def _cache_miss(self, query: str, query_embedding: np.ndarray):
        """
        Lida com um cache miss: gera resposta, adiciona ao índice e ao cache.
        """
        print("Gerando nova resposta com o LLM...")

        # Simula a geração de uma resposta.
        # Em um caso real, você chamaria ollama.generate() ou ollama.chat().
        # Para este teste, vamos apenas criar uma resposta padrão.
        new_response = f"Esta é uma nova resposta para '{query}' gerada em {time.strftime('%H:%M:%S')}"

        # Adiciona o embedding da query ao índice FAISS
        new_id = self.index.ntotal
        self.index.add(query_embedding)

        # Armazena a nova resposta no nosso dicionário de cache
        self.response_cache[new_id] = new_response

        print(f"Nova resposta gerada e adicionada ao cache com ID {new_id}.")
        print(f"✔️ Resposta (nova): '{new_response}'")


# --- Demonstração ---
if __name__ == "__main__":
    # Garanta que o Ollama está rodando com o modelo 'mistral:7b'
    # ollama run mistral:7b

    cache = SemanticCache(dimension=EMBEDDING_DIM, model=OLLAMA_MODEL)

    queries = [
        "Qual a capital da França?",  # Primeira query -> Miss
        "Qual é a capital francesa?",  # Query similar -> Hit
        "Quem escreveu Dom Quixote?", # Nova query -> Miss
        "Qual a principal cidade da França?", # Outra query similar -> Hit
        "Qual a cor do céu?" # Nova query -> Miss
    ]

    for q in queries:
        cache.process_query(q)
        time.sleep(1) # Pausa para facilitar a leitura da saída

"""
RAG System Plugin

This plugin demonstrates a complex Retrieval-Augmented Generation (RAG) system
that uses core nodes internally.
"""

from backend.plugins.base_plugin import BasePlugin

class RAGSystem(BasePlugin):
    """
    A plugin that implements a Retrieval-Augmented Generation (RAG) system.
    """

    __plugin_meta__ = {
        "name": "RAG System",
        "category": "AI_SYSTEMS",
        "description": "Complete Retrieval-Augmented Generation system",
        "editable": True,
        "inputs": {
            "documents": {"type": "array", "description": "Documents to process"},
            "query": {"type": "string", "description": "User query"}
        },
        "outputs": {
            "response": {"type": "string", "description": "Generated response"},
            "sources": {"type": "array", "description": "Source documents used"},
            "embedding_time": {"type": "number", "description": "Time taken for embedding (ms)"},
            "retrieval_time": {"type": "number", "description": "Time taken for retrieval (ms)"},
            "generation_time": {"type": "number", "description": "Time taken for generation (ms)"}
        },
        "configFields": [
            {
                "name": "chunk_size",
                "type": "number",
                "label": "Chunk Size",
                "default": 1000
            },
            {
                "name": "chunk_overlap",
                "type": "number",
                "label": "Chunk Overlap",
                "default": 200
            },
            {
                "name": "embedding_model",
                "type": "select",
                "label": "Embedding Model",
                "options": [
                    {"label": "OpenAI", "value": "openai"},
                    {"label": "Hugging Face", "value": "huggingface"}
                ],
                "default": "openai"
            },
            {
                "name": "retrieval_k",
                "type": "number",
                "label": "Top K Results",
                "default": 3
            },
            {
                "name": "llm_model",
                "type": "string",
                "label": "LLM Model",
                "default": "gpt-3.5-turbo"
            },
            {
                "name": "temperature",
                "type": "number",
                "label": "Temperature",
                "default": 0.7
            }
        ]
    }

    @classmethod
    def run(cls, inputs, config):
        """
        Execute the plugin with the given inputs and configuration.

        Args:
            inputs (dict): Input values from connected nodes
            config (dict): Configuration values set by the user

        Returns:
            dict: Output values to be passed to connected nodes
        """
        import time

        documents = inputs.get("documents", [])
        query = inputs.get("query", "")

        if not documents or not query:
            return {
                "response": "Error: Missing documents or query",
                "sources": [],
                "embedding_time": 0,
                "retrieval_time": 0,
                "generation_time": 0
            }

        # Step 1: Split documents into chunks
        chunks = cls._split_documents(documents, config)

        # Step 2: Create embeddings
        embedding_start = time.time()
        embeddings = cls._embed_chunks(chunks, config)
        embedding_time = (time.time() - embedding_start) * 1000  # Convert to ms

        # Step 3: Retrieve relevant chunks
        retrieval_start = time.time()
        retrieved_chunks = cls._retrieve(query, chunks, embeddings, config)
        retrieval_time = (time.time() - retrieval_start) * 1000  # Convert to ms

        # Step 4: Generate response
        generation_start = time.time()
        response = cls._generate_response(query, retrieved_chunks, config)
        generation_time = (time.time() - generation_start) * 1000  # Convert to ms

        return {
            "response": response,
            "sources": [{"text": chunk, "score": score} for chunk, score in retrieved_chunks],
            "embedding_time": round(embedding_time, 2),
            "retrieval_time": round(retrieval_time, 2),
            "generation_time": round(generation_time, 2)
        }

    @classmethod
    def _split_documents(cls, documents, config):
        """Split documents into chunks using the text splitter core node."""
        chunks = []

        for doc in documents:
            # Use the text splitter core node
            splitter_result = cls.execute_core_node(
                "core.text_splitter",
                {"text": doc},
                {
                    "chunk_size": config.get("chunk_size", 1000),
                    "chunk_overlap": config.get("chunk_overlap", 200)
                }
            )

            if splitter_result and "chunks" in splitter_result:
                chunks.extend(splitter_result["chunks"])
            else:
                # Fallback: simple splitting by newlines and limiting to chunk_size
                chunk_size = config.get("chunk_size", 1000)
                doc_chunks = []

                # Split by paragraphs first
                paragraphs = doc.split("\n\n")
                current_chunk = ""

                for para in paragraphs:
                    if len(current_chunk) + len(para) + 2 <= chunk_size:
                        if current_chunk:
                            current_chunk += "\n\n"
                        current_chunk += para
                    else:
                        if current_chunk:
                            doc_chunks.append(current_chunk)
                        current_chunk = para

                if current_chunk:
                    doc_chunks.append(current_chunk)

                chunks.extend(doc_chunks)

        return chunks

    @classmethod
    def _embed_chunks(cls, chunks, config):
        """Create embeddings for chunks using the embedder core node."""
        # Use the embedder core node
        embedder_result = cls.execute_core_node(
            "core.embedder",
            {"texts": chunks},
            {"model": config.get("embedding_model", "openai")}
        )

        if embedder_result and "embeddings" in embedder_result:
            return embedder_result["embeddings"]
        else:
            # Fallback: return dummy embeddings (in a real implementation,
            # we would use a proper embedding library)
            return [{"index": i, "embedding": [0.1, 0.2, 0.3]} for i in range(len(chunks))]

    @classmethod
    def _retrieve(cls, query, chunks, embeddings, config):
        """Retrieve relevant chunks using the retriever core node."""
        # Use the retriever core node
        retriever_result = cls.execute_core_node(
            "core.retriever",
            {
                "query": query,
                "chunks": chunks,
                "embeddings": embeddings
            },
            {"top_k": config.get("retrieval_k", 3)}
        )

        if retriever_result and "results" in retriever_result:
            return [(chunks[result["index"]], result["score"]) for result in retriever_result["results"]]
        else:
            # Fallback: simple keyword matching
            query_terms = set(query.lower().split())
            scored_chunks = []

            for i, chunk in enumerate(chunks):
                chunk_terms = set(chunk.lower().split())
                overlap = len(query_terms.intersection(chunk_terms))
                if overlap > 0:
                    score = overlap / len(query_terms)
                    scored_chunks.append((chunk, score))

            # Sort by score and take top k
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            return scored_chunks[:config.get("retrieval_k", 3)]

    @classmethod
    def _generate_response(cls, query, retrieved_chunks, config):
        """Generate a response using the LLM core node."""
        # Prepare context from retrieved chunks
        context = "\n\n".join([chunk for chunk, _ in retrieved_chunks])

        # Use the LLM core node
        llm_result = cls.execute_core_node(
            "core.llm",
            {
                "prompt": f"Based on the following context, answer the query.\n\nContext:\n{context}\n\nQuery: {query}\n\nAnswer:"
            },
            {
                "model": config.get("llm_model", "gpt-3.5-turbo"),
                "temperature": config.get("temperature", 0.7)
            }
        )

        if llm_result and "response" in llm_result:
            return llm_result["response"]
        else:
            # Fallback: return a simple response
            return f"I found {len(retrieved_chunks)} relevant documents that might answer your query: '{query}'. However, I cannot generate a detailed response at this time."

    @classmethod
    def generate_code(cls, config):
        """
        Generate code for the plugin.

        Args:
            config (dict): Configuration values set by the user

        Returns:
            str: Generated code
        """
        code = [
            "# RAG System Implementation",
            "import time",
            "",
            "def rag_system(documents, query):",
            f"    # Configuration: chunk_size={config.get('chunk_size', 1000)}, chunk_overlap={config.get('chunk_overlap', 200)}",
            f"    # Configuration: embedding_model='{config.get('embedding_model', 'openai')}', retrieval_k={config.get('retrieval_k', 3)}",
            f"    # Configuration: llm_model='{config.get('llm_model', 'gpt-3.5-turbo')}', temperature={config.get('temperature', 0.7)}",
            "",
            "    # Step 1: Split documents into chunks",
            "    chunks = []",
            "    for doc in documents:",
            "        # Split document into chunks",
            "        # ... (implementation details)",
            "",
            "    # Step 2: Create embeddings",
            "    embeddings = []",
            "    for chunk in chunks:",
            "        # Create embedding for chunk",
            "        # ... (implementation details)",
            "",
            "    # Step 3: Retrieve relevant chunks",
            "    retrieved_chunks = []",
            "    # ... (implementation details)",
            "",
            "    # Step 4: Generate response",
            "    context = '\\n\\n'.join([chunk for chunk, _ in retrieved_chunks])",
            "    prompt = f\"Based on the following context, answer the query.\\n\\nContext:\\n{context}\\n\\nQuery: {query}\\n\\nAnswer:\"",
            "    # Generate response using LLM",
            "    # ... (implementation details)",
            "",
            "    return {",
            "        'response': response,",
            "        'sources': [{'text': chunk, 'score': score} for chunk, score in retrieved_chunks]",
            "    }"
        ]

        return "\n".join(code)

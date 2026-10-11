# import os
# import hashlib
# import chromadb
# from sentence_transformers import SentenceTransformer


# class RAGPipeline:
#     def __init__(self, persist_dir, chunk_size=500, chunk_overlap=50):
#         self.chunk_size = chunk_size
#         self.chunk_overlap = chunk_overlap
#         print("Loading embedding model...")
#         self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#         print("Embedding model ready")
#         os.makedirs(persist_dir, exist_ok=True)
#         self.client = chromadb.PersistentClient(path=persist_dir)
#         self.collection = None

#     def chunk_text(self, text, source):
#         text = text.strip()
#         if not text:
#             return []
#         chunks = []
#         start = 0
#         n = len(text)
#         while start < n:
#             end = min(start + self.chunk_size, n)
#             if end < n:
#                 for sep in [". ", ".\n", "! ", "? ", "\n\n"]:
#                     idx = text.rfind(sep, start + self.chunk_size // 2, end)
#                     if idx != -1:
#                         end = idx + len(sep)
#                         break
#             piece = text[start:end].strip()
#             if piece:
#                 cid = hashlib.md5(f"{source}_{start}".encode()).hexdigest()[:12]
#                 chunks.append({"id": cid, "text": piece,
#                                "metadata": {"source": source, "start": start}})
#             new_start = end - self.chunk_overlap
#             start = new_start if new_start > start else end
#         return chunks

#     def index_documents(self, documents, collection_name="project_docs"):
#         try:
#             self.client.delete_collection(collection_name)
#         except Exception:
#             pass
#         self.collection = self.client.get_or_create_collection(
#             name=collection_name,
#             metadata={"hnsw:space": "cosine"})

#         all_chunks = []
#         for fname, content in documents.items():
#             chunks = self.chunk_text(content, fname)
#             all_chunks.extend(chunks)
#             print(f"  {fname}: {len(chunks)} chunks")

#         texts = [c["text"] for c in all_chunks]
#         print(f"Generating embeddings for {len(texts)} chunks...")
#         embeddings = self.embedder.encode(texts).tolist()
#         self.collection.add(
#             ids=[c["id"] for c in all_chunks],
#             documents=texts,
#             embeddings=embeddings,
#             metadatas=[c["metadata"] for c in all_chunks])
#         print(f"Indexed {len(all_chunks)} chunks")
#         return len(all_chunks)

#     def retrieve(self, query, top_k=3):
#         if self.collection is None:
#             return []
#         q_emb = self.embedder.encode([query]).tolist()
#         res = self.collection.query(query_embeddings=q_emb, n_results=top_k)
#         out = []
#         if res["documents"] and res["documents"][0]:
#             for i, doc in enumerate(res["documents"][0]):
#                 out.append({"text": doc, "source": res["metadatas"][0][i]["source"]})
#         return out

#     def get_context(self, query, top_k=3):
#         results = self.retrieve(query, top_k)
#         if not results:
#             return "No context found."
#         return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in results)



















































































import os
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer


class RAGPipeline:
    def __init__(self, persist_dir, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        print("Loading embedding model...")
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("Embedding model ready")
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None

    def chunk_text(self, text, source):
        text = text.strip()
        if not text:
            return []
        chunks = []
        start = 0
        n = len(text)
        while start < n:
            end = min(start + self.chunk_size, n)
            if end < n:
                for sep in [". ", ".\n", "! ", "? ", "\n\n"]:
                    idx = text.rfind(sep, start + self.chunk_size // 2, end)
                    if idx != -1:
                        end = idx + len(sep)
                        break
            piece = text[start:end].strip()
            if piece:
                cid = hashlib.md5(f"{source}_{start}".encode()).hexdigest()[:12]
                chunks.append({"id": cid, "text": piece,
                               "metadata": {"source": source, "start": start}})
            new_start = end - self.chunk_overlap
            start = new_start if new_start > start else end
        return chunks

    def index_documents(self, documents, collection_name="project_docs",
                        reset=True, append=False):
        """
        Index documents into the vector store.

        Args:
            documents: dict of {filename: content}
            collection_name: name of collection
            reset: if True and append=False, wipe collection first (fresh start)
            append: if True, ADD new chunks to existing collection (incremental)
        """
        if reset and not append:
            try:
                self.client.delete_collection(collection_name)
            except Exception:
                pass

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"})

        # When appending, find out which chunk IDs already exist to avoid duplicates
        existing_ids = set()
        if append and self.collection.count() > 0:
            try:
                existing = self.collection.get()
                existing_ids = set(existing.get("ids", []))
            except Exception:
                existing_ids = set()

        all_chunks = []
        for fname, content in documents.items():
            chunks = self.chunk_text(content, fname)
            new_chunks = [c for c in chunks if c["id"] not in existing_ids]
            all_chunks.extend(new_chunks)
            print(f"  {fname}: {len(new_chunks)} new chunks")

        if not all_chunks:
            print("No new chunks to index")
            return 0

        texts = [c["text"] for c in all_chunks]
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.encode(texts).tolist()
        self.collection.add(
            ids=[c["id"] for c in all_chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[c["metadata"] for c in all_chunks])
        print(f"Indexed {len(all_chunks)} chunks (total: {self.collection.count()})")
        return len(all_chunks)

    def retrieve(self, query, top_k=3):
        if self.collection is None:
            return []
        q_emb = self.embedder.encode([query]).tolist()
        res = self.collection.query(query_embeddings=q_emb, n_results=top_k)
        out = []
        if res["documents"] and res["documents"][0]:
            for i, doc in enumerate(res["documents"][0]):
                out.append({"text": doc, "source": res["metadatas"][0][i]["source"]})
        return out

    def get_context(self, query, top_k=3):
        results = self.retrieve(query, top_k)
        if not results:
            return "No context found."
        return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in results)
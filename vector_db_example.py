import numpy as np
import faiss
import os

class SimpleVectorDB:
    def __init__(self, embedding_dim=384):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)  # L2 distance
        self.documents = []
        self.ids = []
        
        # Try to load MiniLM, fallback to simple embeddings if not available
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_embeddings = True
            print("MiniLM model loaded successfully")
        except Exception as e:
            print(f"Could not load MiniLM model: {e}")
            print("Using simple word count embeddings instead")
            self.use_embeddings = False
        
    def _simple_embedding(self, text):
        """Generate simple word count based embedding"""
        # Simple embedding based on character counts and word features
        words = text.lower().split()
        embedding = np.zeros(self.embedding_dim)
        
        # Use various simple features
        features = [
            len(text),  # text length
            len(words),  # word count
            text.count(' '),  # space count
            sum(1 for c in text if c.isupper()),  # uppercase count
            sum(1 for c in text if c.isdigit()),  # digit count
            text.count('.'),  # period count
            text.count(','),  # comma count
        ]
        
        # Repeat features to fill embedding dimension
        for i, feature in enumerate(features):
            if i < self.embedding_dim:
                embedding[i] = feature
        
        # Fill remaining with word-specific features
        word_idx = len(features)
        common_words = ['the', 'and', 'is', 'to', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this']
        for word in common_words:
            if word_idx >= self.embedding_dim:
                break
            embedding[word_idx] = words.count(word)
            word_idx += 1
            
        return embedding
        
    def add_documents(self, ids, documents):
        """Add documents and automatically generate embeddings"""
        self.ids.extend(ids)
        self.documents.extend(documents)
        
        # Generate embeddings
        if self.use_embeddings:
            embeddings = self.model.encode(documents)
        else:
            embeddings = [self._simple_embedding(doc) for doc in documents]
            
        embeddings_array = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings_array)
        
    def query_by_text(self, query_text, n_results=10):
        """Query by text (automatically generates embedding)"""
        if self.use_embeddings:
            query_embedding = self.model.encode([query_text])
        else:
            query_embedding = [self._simple_embedding(query_text)]
        return self.query(query_embedding, n_results)
        
    def query(self, query_embeddings, n_results=10):
        """Query by vector similarity"""
        query_array = np.array(query_embeddings, dtype=np.float32)
        
        # Search for similar vectors
        distances, indices = self.index.search(query_array, n_results)
        
        results = {
            'ids': [[self.ids[i] for i in idx_row if i != -1] for idx_row in indices],
            'documents': [[self.documents[i] for i in idx_row if i != -1] for idx_row in indices],
            'distances': distances.tolist()
        }
        
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the vector database with MiniLM
    db = SimpleVectorDB()
    
    # Add documents (embeddings are automatically generated)
    db.add_documents(
        ids=["id1", "id2"],
        documents=["This is a document about artificial intelligence", "Another document about machine learning"]
    )
    
    # Query by text (embedding is automatically generated)
    print("Query Results for 'AI technology':")
    results = db.query_by_text("AI technology", n_results=10)
    
    print(f"Found {len(results['ids'][0])} results:")
    for i, (doc_id, document, distance) in enumerate(zip(results['ids'][0], results['documents'][0], results['distances'][0])):
        print(f"  {i+1}. ID: {doc_id}, Document: {document}, Distance: {distance:.4f}")
    
    # Add more documents
    db.add_documents(
        ids=["id3", "id4"],
        documents=["Third document about deep learning neural networks", "Fourth document about data science and analytics"]
    )
    
    # Another query
    print("\nQuery Results for 'neural networks':")
    results2 = db.query_by_text("neural networks", n_results=3)
    
    for i, (doc_id, document, distance) in enumerate(zip(results2['ids'][0], results2['documents'][0], results2['distances'][0])):
        print(f"  {i+1}. ID: {doc_id}, Document: {document}, Distance: {distance:.4f}")

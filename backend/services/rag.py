"""
RAG (Retrieval-Augmented Generation) Service
Uses FAISS for semantic search over offer database
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import json
import os


class OfferRAG:
    """FAISS-based retrieval system for cashback offers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG system.
        
        Args:
            model_name: HuggingFace sentence-transformer model
        """
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.documents = []
        self.index = None
        self.is_initialized = False
    
    def add_offers(self, offers: List[Dict[str, Any]]) -> None:
        """
        Add offers to the vector database.
        
        Args:
            offers: List of offer dicts with 'text' and optional 'id' keys
        """
        if not offers:
            return
        
        # Extract texts
        texts = [offer.get("text", "") for offer in offers]
        
        # Generate embeddings
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype=np.float32)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        self.embeddings = embeddings
        self.documents = offers
        self.is_initialized = True
        
        print(f"✓ Added {len(offers)} offers to RAG database")
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar offers.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of (offer_dict, similarity_score) tuples
        """
        if not self.is_initialized or len(self.documents) == 0:
            return []
        
        # Encode query
        query_embedding = self.model.encode(query, normalize_embeddings=True)
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            # FAISS L2 distance: convert to similarity score (lower distance = higher similarity)
            similarity = 1 / (1 + distance)
            results.append((self.documents[idx], float(similarity)))
        
        return results
    
    def find_similar_offers(self, offer_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find offers similar to the given text.
        Returns only the offers without scores.
        """
        results = self.search(offer_text, top_k)
        return [offer for offer, _ in results]
    
    def save(self, filepath: str) -> None:
        """Save FAISS index and documents to disk"""
        if not self.is_initialized:
            return
        
        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save index
        index_path = filepath.replace(".json", ".index")
        faiss.write_index(self.index, index_path)
        
        # Save documents
        with open(filepath, "w") as f:
            json.dump(self.documents, f, indent=2)
        
        print(f"✓ RAG database saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load FAISS index and documents from disk"""
        index_path = filepath.replace(".json", ".index")
        
        if not os.path.exists(index_path) or not os.path.exists(filepath):
            return
        
        # Load documents
        with open(filepath, "r") as f:
            self.documents = json.load(f)
        
        # Load index
        self.index = faiss.read_index(index_path)
        self.is_initialized = True
        
        print(f"✓ RAG database loaded from {filepath}")


# Global RAG instance
_rag_instance = None


def get_rag_instance() -> OfferRAG:
    """Get or create global RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = OfferRAG()
    return _rag_instance


def initialize_rag_with_offers(offers: List[Dict[str, Any]]) -> None:
    """Initialize RAG with a list of offers"""
    rag = get_rag_instance()
    rag.add_offers(offers)


def search_similar_offers(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for similar offers"""
    rag = get_rag_instance()
    return rag.find_similar_offers(query, top_k)


if __name__ == "__main__":
    # Test RAG system
    sample_offers = [
        {
            "id": 1,
            "text": "10% cashback up to ₹100 on min ₹500 using HDFC card first transaction"
        },
        {
            "id": 2,
            "text": "5% cashback on Amazon purchases with ICICI credit card"
        },
        {
            "id": 3,
            "text": "₹500 flat cashback on ₹5000+ spend with SBI debit card"
        },
        {
            "id": 4,
            "text": "3% cashback on all online transactions with Axis bank"
        },
    ]
    
    rag = OfferRAG()
    rag.add_offers(sample_offers)
    print(f"✓ RAG initialized with {len(sample_offers)} offers\n")
    
    # Test search
    query = "cashback on first purchase with HDFC"
    results = rag.search(query, top_k=2)
    
    print(f"Query: {query}")
    print(f"Top results:")
    for offer, similarity in results:
        print(f"  - {offer['text']}")
        print(f"    Similarity: {similarity:.2%}\n")

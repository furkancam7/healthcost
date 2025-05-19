import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import pandas as pd
import json
from typing import List, Dict, Any, Optional, Union
import os
import numpy as np
import torch

class HealthDataRAG:
    def __init__(self, api_key: str):
        """Initialize the RAG system for health data."""
        # Initialize ChromaDB client
        self.client = chromadb.Client()
        
        # Create or get collection with default embedding function
        self.collection = self.client.get_or_create_collection(
            name="health_costs"
        )
        
        # Load initial data
        self._load_initial_data()
    
    def _load_initial_data(self):
        """Load initial health cost data into the vector database."""
        # Load costs data
        costs_df = pd.read_csv('data/health_costs.csv')
        
        # Convert costs data to documents
        for _, row in costs_df.iterrows():
            doc = f"Region: {row['region']}, Age Group: {row['age_group']}, Base Cost: ${row['base_cost']}"
            self.collection.add(
                documents=[doc],
                metadatas=[{
                    'region': row['region'],
                    'age_group': row['age_group'],
                    'base_cost': float(row['base_cost'])
                }],
                ids=[f"cost_{row['region']}_{row['age_group']}"]
            )
        
        # Load weights data
        with open('data/chronic_condition_weights.json', 'r') as f:
            weights = json.load(f)
        
        # Convert weights data to documents
        for condition, weight in weights.items():
            doc = f"Chronic Condition: {condition}, Risk Weight: {weight}"
            self.collection.add(
                documents=[doc],
                metadatas=[{
                    'condition': condition,
                    'weight': float(weight)
                }],
                ids=[f"weight_{condition}"]
            )
    
    def get_relevant_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the vector database."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results or 'documents' not in results or 'metadatas' not in results:
                return []
            
            if not results['documents'] or not results['metadatas']:
                return []
                
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            return [
                {
                    'text': doc,
                    'metadata': meta
                }
                for doc, meta in zip(documents, metadatas)
            ]
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return []
    
    def get_cost_data(self, region: str, age_group: str) -> Optional[float]:
        """Get base cost for a specific region and age group."""
        query = f"Region: {region}, Age Group: {age_group}"
        results = self.get_relevant_context(query, n_results=1)
        
        if not results or not results[0].get('metadata'):
            return None
            
        return results[0]['metadata'].get('base_cost')
    
    def get_condition_weight(self, condition: str) -> Optional[float]:
        """Get risk weight for a specific chronic condition."""
        query = f"Chronic Condition: {condition}"
        results = self.get_relevant_context(query, n_results=1)
        
        if not results or not results[0].get('metadata'):
            return None
            
        return results[0]['metadata'].get('weight') 
"""Real estate matching system."""

import os
from typing import List, Dict, Any


from langchain_community.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS


class RealEstateAgent:
    """Handles real estate listing generation and matching."""

    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            openai_api_base=os.getenv(
                "OPENAI_API_BASE", "https://openai.vocareum.com/v1"),
            openai_api_key=os.getenv(
                "OPENAI_API_KEY", "voc-73934113126677372266267671b469979c3.45097448")
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.vector_store = None

    def generate_listings(self, num_listings: int = 10) -> List[Dict[str, Any]]:
        """Generate real estate listings."""
        try:
            prompt = self._generate_listing_prompt()
            listings = []
            for _ in range(num_listings):
                try:
                    response = self.llm.invoke(prompt).content
                    listings.append(self._parse_listing(response.strip()))
                except (ValueError, RuntimeError) as e:
                    print(f"Error generating listing: {e}")
                    continue
            return listings
        except ValueError as err:
            print(f"Error generating listings: {err}")
            return []

    def process_buyer_preferences(self, preferences: List[str]) -> str:
        """Process buyer preferences into a search query."""
        prompt = f"Summarize the ideal home given: {' '.join(preferences)}"
        return self.llm.invoke(prompt).content.strip()

    def personalize_description(self, listing: Dict[str, Any], preferences: List[str]) -> str:
        """Personalize listing description for buyer."""
        prompt = f"""Personalize this listing for the buyer:
        Listing: {listing}
        Buyer Preferences: {' '.join(preferences)}"""
        return self.llm.invoke(prompt).content.strip()

    def _generate_listing_prompt(self) -> str:
        """Get prompt for generating a listing."""
        return """Generate a detailed real estate listing with:
               Neighborhood: [name], Price: [USD], Bedrooms: [number],
               Bathrooms: [number], House Size: [sqft],
               Description: [property description],  
               Neighborhood Description: [description]"""

    def _parse_listing(self, raw_listing: str) -> Dict[str, str]:
        """Parse raw listing text into structured format."""
        parsed = {}
        for line in raw_listing.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                parsed[key.strip()] = value.strip()
        return parsed

    def store_listings(self, listings: List[Dict[str, Any]]) -> None:
        """Store listings in vector store."""
        texts = [f"{l['Description']} {l['Neighborhood Description']}"
                 for l in listings]
        metadatas = [{k: v for k, v in l.items() if k != 'Description'}
                     for l in listings]
        self.vector_store = FAISS.from_texts(
            texts, self.embeddings, metadatas=metadatas)

    def find_matches(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Find matching listings based on preferences."""
        if not self.vector_store:
            return []
        docs = self.vector_store.similarity_search(query, k=k)
        return [{**doc.metadata, 'Description': doc.page_content} for doc in docs]

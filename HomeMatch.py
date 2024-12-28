"""HomeMatch: Real estate listing generation, storage, and matching."""

import os
from typing import List, Dict, Optional
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Set OpenAI API configurations
os.environ["OPENAI_API_BASE"] = "https://openai.vocareum.com/v1"
os.environ["OPENAI_API_KEY"] = "voc-73934113126677372266267671b469979c3.45097448"


class HomeMatch:
    """Handles real estate listing generation, storage, and matching."""

    def __init__(self) -> None:
        """Initialize LLM, embeddings, and vector store."""
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo",
                              openai_api_base=os.environ["OPENAI_API_BASE"],
                              openai_api_key=os.environ["OPENAI_API_KEY"])
        self.embeddings = OpenAIEmbeddings(openai_api_base=os.environ["OPENAI_API_BASE"],
                                           openai_api_key=os.environ["OPENAI_API_KEY"])
        self.vector_store: Optional[FAISS] = None

    def generate_listings(self, num_listings: int = 3) -> List[Dict]:
        """Generate real estate listings using LLM."""
        try:
            messages = [
                {"role": "user", "content": self._generate_listing_prompt()}]
            return [self._parse_listing(self.llm.predict_messages(messages).content)
                    for _ in range(min(num_listings, 3))]
        except ValueError as err:
            print(f"Warning: Using default listings. Error: {str(err)}")
            return self._parse_listings(self._get_default_listings())

    def _generate_listing_prompt(self) -> str:
        """Get prompt for generating a real estate listing."""
        return """Generate a detailed real estate listing with the format:
               Neighborhood: [name]
               Price: [price in USD]
               Bedrooms: [number] 
               Bathrooms: [number]
               House Size: [size in sqft]  
               Description: [property description]
               Neighborhood Description: [neighborhood description]"""

    def _get_default_listings(self) -> List[str]:
        """Return default listings if API fails."""
        return ["""Neighborhood: Maple Valley
       Price: $650,000
       Bedrooms: 3
       Bathrooms: 2.5
       House Size: 2,200 sqft
       Description: Modern home with open-concept kitchen.
       Neighborhood Description: Family-friendly area with schools."""]

    def _parse_listing(self, raw_listing: str) -> Dict:
        """Parse raw listing text into structured format."""
        lines = raw_listing.strip().split('\n')
        parsed = {}
        current_key = None
        current_value = []
        for line in lines:
            if ':' in line and not current_value:
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()
                if key in ['Description', 'Neighborhood Description']:
                    current_key = key
                    current_value.append(value)
                else:
                    parsed[key] = value
            elif current_key:
                current_value.append(line.strip())
            if current_key and (not line.strip() or line == lines[-1]):
                parsed[current_key] = ' '.join(current_value).strip()
                current_key = None
                current_value = []
        return parsed

    def _parse_listings(self, raw_listings: List[str]) -> List[Dict]:
        """Parse multiple raw listings."""
        return [self._parse_listing(listing) for listing in raw_listings]

    def store_listings(self, listings: List[Dict]) -> None:
        """Store listings in vector store."""
        texts = [
            f"{l.get('Description', '')} {
                l.get('Neighborhood Description', '')}"
            for l in listings
        ]
        metadatas = [
            {k: v for k, v in l.items()
             if k not in ['Description', 'Neighborhood Description']}
            for l in listings
        ]
        self.vector_store = FAISS.from_texts(
            texts, self.embeddings, metadatas=metadatas)

    def process_buyer_preferences(self, user_preferences: List[str]) -> str:
        """Process buyer preferences into a search query."""
        prompt = f"""Given these preferences: {' '.join(user_preferences)}
        Create a summary of the ideal home for this buyer."""
        return self.llm.predict_messages([{"role": "user", "content": prompt}]).content

    def find_matches(self, search_query: str, num_results: int = 3) -> List[Dict]:
        """Find matching listings based on preferences."""
        if not self.vector_store:
            return []
        results = self.vector_store.similarity_search(
            search_query, k=num_results)
        return [{**doc.metadata, 'Description': doc.page_content} for doc in results]

    def personalize_description(self, listing: Dict, user_preferences: List[str]) -> str:
        """Personalize listing description for buyer."""
        prompt = f"""Given preferences: {' '.join(user_preferences)}
        And listing: {listing}
        Rewrite to highlight relevant features."""
        return self.llm.predict_messages([{"role": "user", "content": prompt}]).content


def run_homematch(buyer_preferences: List[str], num_listings: int = 3) -> List[Dict]:
    """Run the HomeMatch application workflow."""
    try:
        home_match = HomeMatch()
        print("Generating listings...")
        listings = home_match.generate_listings(num_listings)
        print("Storing listings...")
        home_match.store_listings(listings)
        try:
            print("Processing preferences...")
            search_query = home_match.process_buyer_preferences(
                buyer_preferences)
        except ValueError as err:
            print(f"Using simplified matching: {err}")
            search_query = " ".join(buyer_preferences)
        print("Finding matches...")
        found_matches = home_match.find_matches(
            search_query, num_results=min(3, num_listings))
        print("Personalizing descriptions...")
        return [home_match.personalize_description(match, buyer_preferences)
                for match in found_matches]
    except KeyError as err:
        print(f"Error running HomeMatch: {str(err)}")
        return []


if __name__ == "__main__":
    sample_preferences = [
        "Three-bedroom house with spacious kitchen",
        "Quiet neighborhood with good schools",
        "Backyard and two-car garage",
        "Close to public transportation",
        "Suburban feel with urban amenities"
    ]
    final_matches = run_homematch(sample_preferences)
    for i, current_match in enumerate(final_matches, 1):
        print(f"\nMatch {i}:")
        print(current_match)
        print("-" * 80)

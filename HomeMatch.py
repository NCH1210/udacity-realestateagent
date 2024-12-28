"""HomeMatch: Real estate listing generation, storage, and matching."""

import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

os.environ["OPENAI_API_BASE"] = "https://openai.vocareum.com/v1"
os.environ["OPENAI_API_KEY"] = "voc-73934113126677372266267671b469979c3.45097448"


class HomeMatch:
    """Handles real estate listing generation, storage, and matching."""

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo",
                              openai_api_base=os.environ["OPENAI_API_BASE"],
                              openai_api_key=os.environ["OPENAI_API_KEY"])
        self.embeddings = OpenAIEmbeddings(openai_api_base=os.environ["OPENAI_API_BASE"],
                                           openai_api_key=os.environ["OPENAI_API_KEY"])
        self.vector_store = None

    def generate_listings(self, num_listings=10):
        """Generate real estate listings using LLM."""
        try:
            prompt = self._generate_listing_prompt()
            return [self._parse_listing(self.llm.predict(prompt).strip())
                    for _ in range(num_listings)]
        except ValueError as err:
            print(f"Error generating listings: {err}")
            return []

    def _generate_listing_prompt(self):
        """Get prompt for generating a real estate listing."""
        return """Generate a detailed real estate listing with:
               Neighborhood: [name], Price: [USD], Bedrooms: [number], 
               Bathrooms: [number], House Size: [sqft],
               Description: [property description],
               Neighborhood Description: [description]"""

    def _parse_listing(self, raw_listing):
        """Parse raw listing text into structured format."""
        parsed = {}
        for line in raw_listing.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                parsed[key.strip()] = value.strip()
        return parsed

    def store_listings(self, listings):
        """Store listings in vector store."""
        texts = [f"{l['Description']} {
            l['Neighborhood Description']}" for l in listings]
        metadatas = [{k: v for k, v in l.items() if k != 'Description'}
                     for l in listings]
        self.vector_store = FAISS.from_texts(
            texts, self.embeddings, metadatas=metadatas)

    def process_buyer_preferences(self, preferences):
        """Process buyer preferences into a search query."""
        prompt = f"Summarize the ideal home given: {' '.join(preferences)}"
        return self.llm.predict(prompt).strip()

    def find_matches(self, query, k=3):
        """Find matching listings based on preferences."""
        if not self.vector_store:
            return []
        docs = self.vector_store.similarity_search(query, k=k)
        return [{**doc.metadata, 'Description': doc.page_content} for doc in docs]

    def personalize_description(self, listing, preferences):
        """Personalize listing description for buyer."""
        prompt = f"""Personalize this listing for the buyer:
        Listing: {listing}
        Buyer Preferences: {' '.join(preferences)}"""
        return self.llm.predict(prompt).strip()


def run_homematch(buyer_preferences, num_listings=10):
    """Run the HomeMatch application workflow."""
    homematch = HomeMatch()
    print("Generating listings...")
    listings = homematch.generate_listings(num_listings)
    print(f"Generated {len(listings)} listings. Saving to listings.txt")
    with open('listings.txt', 'w', encoding='utf-8') as f:
        for listing in listings:
            f.write(str(listing) + '\n\n')
    print("Storing listings in vector DB...")
    homematch.store_listings(listings)
    print("Finding personalized matches...")
    query = homematch.process_buyer_preferences(buyer_preferences)
    matches = homematch.find_matches(query)
    print("Generating personalized descriptions...")
    return [homematch.personalize_description(m, buyer_preferences) for m in matches]


if __name__ == '__main__':
    sample_preferences = [
        "Spacious 3BR house with nice kitchen",
        "Quiet neighborhood with good schools",
        "Backyard, garage, energy-efficient",
        "Near public transit and highway",
        "Suburban feel with urban amenities"
    ]
    personalized_matches = run_homematch(sample_preferences)
    print(f"\nGenerated {len(personalized_matches)} personalized matches:")
    for i, match in enumerate(personalized_matches, 1):
        print(f"\nMatch {i}:\n{match}\n{'-'*50}")

"""
Real estate listing generator that uses LLM to create and personalize listings based on 
buyer preferences.
"""

import json
import time
from typing import List, Dict, Tuple

from openai import OpenAI, OpenAIError, APIError, APIConnectionError


class ListingGenerator:
    """Generates and personalizes real estate listings using OpenAI's GPT model."""

    def __init__(self):
        """Initialize with Vocareum OpenAI client."""
        self.client = OpenAI(
            base_url="https://openai.vocareum.com/v1",
            api_key="voc-00000000000000000000000000000000abcd.12345678"
        )

        self.base_prompt = (
            "Generate a realistic real estate listing in JSON format with the following fields:\n"
            "- neighborhood\n"
            "- price (between $300,000 and $2,000,000)\n"
            "- bedrooms (1-6)\n"
            "- bathrooms (1-4)\n"
            "- houseSize (in sqft, between 800 and 5000)\n"
            "- description (detailed property description)\n"
            "- neighborhoodDescription (detailed area description)\n"
            "- features (list of key property features)\n"
            "- yearBuilt (between 1900 and 2024)\n"
            "- propertyType (e.g., Single Family Home, Condo, Townhouse)\n"
            "- lotSize (in acres or sqft)\n"
            "- amenities (list of nearby amenities)\n"
            "- parkingType (e.g., garage, carport, street parking)\n"
            "- schoolDistrict\n\n"
            "Create a unique listing with specific details and character.\n"
            "Ensure all numeric values are realistic and consistent.\n"
            "The description should paint a vivid picture of the property."
        )

    def generate_listing(self, style_prompt: str = "") -> Dict:
        """Generate a single listing with optional style guidance."""
        try:
            full_prompt = self.base_prompt
            if style_prompt:
                full_prompt += f"\nAdditional style guidance: {style_prompt}"

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a real estate listing generator that creates "
                        "detailed, accurate property descriptions in JSON format."
                    },
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.8
            )

            listing_text = response.choices[0].message.content.strip()
            return json.loads(listing_text)

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
        except (OpenAIError, APIError, APIConnectionError) as e:
            print(f"OpenAI API error: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error processing response: {e}")
            return None

    def calculate_match_score(self, listing: Dict, preferences: Dict) -> float:
        """Calculate how well a listing matches buyer preferences."""
        score = 0.0
        total_weight = 0

        # Price match (high weight)
        if preferences.get('budget'):
            total_weight += 5
            if listing['price'] <= preferences['budget']:
                price_ratio = 1 - (listing['price'] / preferences['budget'])
                # Higher score for lower prices
                score += 5 * (0.5 + price_ratio/2)

        # Bedroom match (high weight)
        if preferences.get('min_bedrooms'):
            total_weight += 4
            if listing['bedrooms'] >= preferences['min_bedrooms']:
                score += 4

        # Feature matches (medium weight)
        if preferences.get('desired_features'):
            total_weight += 3
            features_lower = [f.lower() for f in listing['features']]
            for feature in preferences['desired_features']:
                if any(feature.lower() in f for f in features_lower):
                    score += 3/len(preferences['desired_features'])

        # Location preferences (medium weight)
        if preferences.get('location_preferences'):
            total_weight += 3
            combined_desc = (f"{listing['neighborhoodDescription']} "
                             f"{listing['description']}")
            for pref in preferences['location_preferences']:
                if pref.lower() in combined_desc.lower():
                    score += 3/len(preferences['location_preferences'])

        # Must-haves (highest weight)
        if preferences.get('must_haves'):
            total_weight += 6
            combined_text = (
                f"{listing['description']} {
                    listing['neighborhoodDescription']} "
                f"{' '.join(listing['features'])}"
            )
            for must_have in preferences['must_haves']:
                if must_have.lower() in combined_text.lower():
                    score += 6/len(preferences['must_haves'])

        return score / total_weight if total_weight > 0 else 0

    def personalize_description(
        self,
        listing: Dict,
        preferences: Dict,
        match_score: float
    ) -> str:
        """Generate a personalized description using GPT based on preferences and match score."""
        try:
            personalization_prompt = (
                "Act as a skilled real estate agent crafting a personalized "
                "property description.\n\n"
                f"Original Property Details:\n{
                    json.dumps(listing, indent=2)}\n\n"
                f"Buyer Preferences:\n{json.dumps(preferences, indent=2)}\n\n"
                f"Match Score: {match_score:.2f} out of 1.0\n\n"
                "Task: Create a personalized description that:\n"
                "1. Highlights specific features that match the buyer's preferences\n"
                "2. Maintains absolute factual accuracy - never add or modify features\n"
                "3. Organizes information in order of relevance to this buyer\n"
                "4. Addresses their must-haves explicitly\n"
                "5. Explains how the property supports their lifestyle preferences\n"
                "6. Uses engaging, professional language\n"
                "7. Includes a brief section about value proposition if under budget\n"
                "8. Maintains a natural, conversational tone\n\n"
                "Format the response in these sections:\n"
                "1. Opening Hook (tailored to their primary interests)\n"
                "2. Key Features (aligned with their preferences)\n"
                "3. Lifestyle Benefits (based on their preferences)\n"
                "4. Neighborhood Highlights (relevant to their needs)\n"
                "5. Value Proposition (if applicable)\n\n"
                "Remember: Focus on EXISTING features that match their preferences. "
                "Never invent or assume features."
            )

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert real estate agent who excels at "
                        "matching properties to buyer preferences while "
                        "maintaining strict factual accuracy."
                    },
                    {"role": "user", "content": personalization_prompt}
                ],
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except (OpenAIError, APIError, APIConnectionError) as e:
            print(f"OpenAI API error: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error processing response: {e}")
            return None

    def search_and_personalize_listings(
        self,
        preferences: Dict
    ) -> List[Tuple[Dict, str, float]]:
        """Generate listings, score them, and create personalized descriptions."""
        listings = []
        styles = [
            "luxury waterfront property",
            "cozy starter home",
            "urban loft with modern amenities",
            "historic property with character",
            "family-friendly suburban home",
            "eco-friendly sustainable house",
            "mountain retreat",
            "golf course community property",
            "downtown penthouse",
            "smart home with cutting-edge technology"
        ]

        for style in styles:
            listing = self.generate_listing(style)
            if listing:
                match_score = self.calculate_match_score(listing, preferences)

                if match_score >= 0.4:  # Threshold for personalization
                    personalized = self.personalize_description(
                        listing,
                        preferences,
                        match_score
                    )
                    listings.append((listing, personalized, match_score))
                time.sleep(1)  # Respect API rate limits

        listings.sort(key=lambda x: x[2], reverse=True)
        return listings

    def save_results_to_file(
        self,
        results: List[Tuple[Dict, str, float]],
        preferences: Dict,
        filename: str = "listings.txt"
    ) -> None:
        """Save all results including match scores and buyer preferences."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Real Estate Listings - Personalized Matches\n\n")

                f.write("## Buyer Preferences\n")
                f.write(f"```json\n{json.dumps(
                    preferences, indent=2)}\n```\n\n")

                for i, (listing, personalized, score) in enumerate(results, 1):
                    f.write(f"## Listing {i} - Match Score: {score:.2f}\n\n")

                    f.write("### Original Listing\n")
                    f.write(f"```json\n{json.dumps(
                        listing, indent=2)}\n```\n\n")

                    f.write("### Personalized Description\n")
                    f.write(f"{personalized}\n\n")
                    f.write("-" * 80 + "\n\n")

            print(f"Successfully saved {
                  len(results)} matched listings to {filename}")

        except IOError as e:
            print(f"Error saving to file: {e}")


def main():
    """Main function to demonstrate the listing search and personalization workflow."""
    preferences = {
        "budget": 800000,
        "min_bedrooms": 3,
        "desired_features": [
            "home office space",
            "modern kitchen",
            "outdoor living area"
        ],
        "lifestyle_preferences": [
            "work from home",
            "enjoys entertaining",
            "active lifestyle"
        ],
        "location_preferences": [
            "walkable neighborhood",
            "close to parks",
            "quiet street"
        ],
        "must_haves": [
            "high-speed internet",
            "good natural light",
            "storage space"
        ]
    }

    generator = ListingGenerator()
    results = generator.search_and_personalize_listings(preferences)

    if results:
        generator.save_results_to_file(results, preferences)


if __name__ == "__main__":
    main()

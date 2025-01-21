"""
Real estate listing management system

"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class PropertyFacts:
    """Container for property-specific facts."""
    lot_size: str
    garage: str
    features: List[str]
    school_district: str
    amenities: List[str]


@dataclass
class Property:
    """Container for property information."""
    id: str
    price: int
    sqft: int
    bedrooms: int
    bathrooms: int
    year_built: int
    location: str
    property_type: str
    facts: PropertyFacts


def create_base_listings() -> List[Property]:
    """Create and return the base set of property listings."""
    return [
        Property(
            id="L1",
            price=1250000,
            sqft=3800,
            bedrooms=5,
            bathrooms=4.5,
            year_built=2018,
            location="Harbor View Estates",
            property_type="Single Family Home",
            facts=PropertyFacts(
                lot_size="0.5 acres",
                garage="3-car attached",
                features=[
                    "Gourmet kitchen with island",
                    "Smart home technology",
                    "Wine cellar",
                    "Home theater"
                ],
                school_district="Harbor View District",
                amenities=[
                    "Private dock",
                    "Beach access",
                    "Gated community",
                    "Tennis courts"
                ]
            )
        ),
        Property(
            id="L2",
            price=575000,
            sqft=1200,
            bedrooms=2,
            bathrooms=2,
            year_built=2015,
            location="Arts District",
            property_type="Loft Condo",
            facts=PropertyFacts(
                lot_size="N/A",
                garage="2 assigned parking spaces",
                features=[
                    "Floor-to-ceiling windows",
                    "Exposed brick walls",
                    "Custom lighting",
                    "High ceilings"
                ],
                school_district="Central District",
                amenities=[
                    "Rooftop terrace",
                    "24/7 security",
                    "Fitness center",
                    "Coffee shop downstairs"
                ]
            )
        ),
        # Add remaining properties here with the same structure...
    ]


def write_listings_to_file(properties: List[Property], filename: str = "listings.txt"):
    """
    Write property listings to a text file in a formatted manner.

    Args:
        properties: List of Property objects
        filename: Name of the output file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Real Estate Listings\n\n")

        for i, prop in enumerate(properties, 1):
            # Write property header
            f.write(f"{i}. {prop.property_type.upper()
                            } - {prop.location.upper()}\n")

            # Write basic details
            f.write(f"   * ID: {prop.id}\n")
            f.write(f"   * Price: ${prop.price:,}\n")
            f.write(f"   * Square Feet: {prop.sqft:,}\n")
            f.write(f"   * Bedrooms: {prop.bedrooms}\n")
            f.write(f"   * Bathrooms: {prop.bathrooms}\n")
            f.write(f"   * Year Built: {prop.year_built}\n")
            f.write(f"   * Location: {prop.location}\n")
            f.write(f"   * Property Type: {prop.property_type}\n")

            # Write property facts
            f.write(f"   * Lot Size: {prop.facts.lot_size}\n")
            f.write(f"   * Garage: {prop.facts.garage}\n")
            f.write(f"   * Features: {', '.join(prop.facts.features)}\n")
            f.write(f"   * School District: {prop.facts.school_district}\n")
            f.write(f"   * Amenities: {', '.join(prop.facts.amenities)}\n")

            # Add blank line between listings
            f.write("\n")


def generate_listing_description(property_data: Property,
                                 preferences: Dict[str, any]) -> str:
    """
    Generate a personalized description based on property facts and buyer preferences.
    """
    base_text = f"""
{property_data.property_type} in {property_data.location}
${property_data.price:,} | {property_data.sqft} sq.ft | \
{property_data.bedrooms} bed | {property_data.bathrooms} bath
Built in {property_data.year_built}

Key Features:
- {', '.join(property_data.facts.features)}
- {property_data.facts.garage}
- Lot Size: {property_data.facts.lot_size}
    """

    enhancements = []

    if preferences.get('family_size'):
        if (preferences['family_size'] >= 4 and
                property_data.bedrooms >= 4):
            enhancements.append(
                f"Perfect for your family of {preferences['family_size']}, "
                f"with {property_data.bedrooms} spacious bedrooms."
            )

    if preferences.get('commute_preference') == 'public_transit':
        if 'Public transit' in property_data.facts.amenities:
            enhancements.append(
                "Ideal for commuters, with convenient public "
                "transportation options nearby."
            )

    if preferences.get('lifestyle') == 'active':
        if 'Park nearby' in property_data.facts.amenities:
            enhancements.append(
                "Perfect for an active lifestyle with parks and "
                "outdoor recreation areas within walking distance."
            )

    result = base_text
    if enhancements:
        result += "\nPersonalized Highlights:\n" + "\n".join(
            f"• {enhancement}" for enhancement in enhancements
        )

    return result


def search_listings(preferences: Dict[str, any],
                    available_listings: List[Property] = None) -> List[Property]:
    """
    Search and rank listings based on buyer preferences.
    """
    if available_listings is None:
        available_listings = create_base_listings()

    def calculate_match_score(prop: Property) -> int:
        """Calculate how well a property matches preferences."""
        score = 0

        if (preferences.get('max_price') and
                prop.price <= preferences['max_price']):
            score += 10

        if (preferences.get('min_sqft') and
                prop.sqft >= preferences['min_sqft']):
            score += 5

        if (preferences.get('min_bedrooms') and
                prop.bedrooms >= preferences['min_bedrooms']):
            score += 5

        if preferences.get('preferred_location'):
            if (preferences['preferred_location'].lower() in
                    prop.location.lower()):
                score += 8

        return score

    scored_properties = [
        (prop, calculate_match_score(prop))
        for prop in available_listings
    ]
    scored_properties.sort(key=lambda x: x[1], reverse=True)

    return [prop for prop, score in scored_properties if score > 0]


def main():
    """Generate listings file and demonstrate search functionality."""
    # Create listings and write to file
    listings = create_base_listings()
    write_listings_to_file(listings)

    # Example search
    sample_preferences = {
        "max_price": 800000,
        "min_sqft": 2000,
        "min_bedrooms": 3,
        "family_size": 4,
        "lifestyle": "active",
        "commute_preference": "public_transit",
        "preferred_location": "Riverside"
    }

    matches = search_listings(sample_preferences)

    for prop in matches:
        description = generate_listing_description(prop, sample_preferences)
        print("\n" + "="*50 + "\n")
        print(description)


if __name__ == "__main__":
    main()

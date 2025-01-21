# udacity-realestateagent

# HomeMatch

HomeMatch is an AI-powered real estate application that generates personalized property listings and matches them to buyer preferences. The system creates detailed, realistic property descriptions and enhances them based on specific buyer requirements while maintaining factual accuracy.

## Features

-   Generates diverse and realistic property listings
-   Personalizes property descriptions based on buyer preferences
-   Matches listings to buyers using a sophisticated scoring system
-   Maintains factual accuracy while highlighting relevant features
-   Exports formatted listings to easily readable text files

## Setup

1. Clone the repo
2. Install dependencies:
    ```
    python==3.7+
    ```
3. The system uses standard Python libraries only - no external dependencies required
4. Run the application:
    ```
    python home_match.py
    ```

## Usage

1. Specify buyer preferences in the preference dictionary:
    ```python
    preferences = {
        "max_price": 800000,
        "min_sqft": 2000,
        "min_bedrooms": 3,
        "family_size": 4,
        "lifestyle": "active",
        "commute_preference": "public_transit",
        "preferred_location": "Riverside"
    }
    ```
2. Run the script to generate matches and enhance descriptions
3. View the complete property listings in `listings.txt`
4. Review personalized matches in the console output

## Components

-   `home_match.py`: Main application code
-   `listings.txt`: Generated property listings
-   Property types include:
    -   Luxury waterfront estates
    -   Modern downtown lofts
    -   Suburban family homes
    -   Historic properties
    -   Mountain retreats
    -   Starter homes
    -   Waterfront cottages
    -   Eco-friendly homes
    -   Urban micro-apartments
    -   Golf course villas

## Requirements

-   Python 3.7+
-   No external dependencies required

## License

This project is licensed under the MIT License.

# udacity-realestateagent

# HomeMatch

HomeMatch is an AI-powered real estate application that generates personalized property listings based on buyer preferences. It uses large language models (LLMs) to create realistic listings, stores them in a vector database, and retrieves semantically relevant matches tailored to each buyer.

## Features

-   Generates diverse property listings with LLMs
-   Stores listings in a vector database for efficient similarity search
-   Matches listings to buyers based on their unique preferences
-   Personalizes listing descriptions to highlight relevant features

## Setup

1. Clone the repo
2. Install dependencies:
    ```
    # Existing Repository Requirements
    langchain=0.0.305
    openai=0.28.1
    pydantic>=1.10.12
    pytest>=7.4.0
    sentence-transformers>=2.2.0
    transformers>=4.31.0
    chromadb==0.4.12
    jupyter==1.0.0
    tiktoken==0.4.0
    ```
3. Set your OpenAI API key in the `OPENAI_API_KEY` environment variable
4. Run the application:
    ```
    python homematch.py
    ```

## Usage

1. Enter buyer preferences as a list of strings in `sample_preferences`
2. Adjust `num_listings` to change the number of listings generated (default 10)
3. Run the script to generate personalized matches
4. View the generated listings in `listings.txt`

## Requirements

-   Python 3.7+
-   OpenAI API key
-   langchain
-   faiss-cpu

## License

This project is licensed under the MIT License.

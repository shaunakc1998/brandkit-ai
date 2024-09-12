# AI BrandKit Generator 

The **AI Brand Kit Generator** is a powerful tool designed to help businesses and individuals create a comprehensive brand identity with minimal effort. The tool leverages advanced AI models to generate a full brand kit based on user input, including logo designs, color palettes, font themes, and taglines.

## Project Overview
This project combines multiple AI services to create a seamless brand identity generation process:
- **Streamlit** is used to build an intuitive user interface that allows users to input their brand details.
- **OpenAI** provides logo generation via DALL-E, allowing the creation of unique, visually striking logos tailored to the brand's identity.
- **Anthropic's Claude** generates a structured brand kit, including color schemes, font recommendations, and taglines based on user input and brand personality.
- **Pinecone** is used to find similar brands using vector similarity search, offering insights from existing brands in similar industries.

The tool outputs:
- A **logo** (generated using OpenAI's DALL-E)
- A **color palette** with explanations for each color choice
- Recommended **fonts** for headings, body text, and accents
- A catchy **tagline** that aligns with the brand's identity and industry

## How It Works
1. **User Inputs**: The user provides details about their brand, including the brand name, description, industry, keywords, and personality type.
2. **AI-Powered Brand Kit Generation**: The system uses AI models (Claude by Anthropic) to generate a detailed brand kit based on the user input, including color themes, fonts, and a tagline.
3. **Logo Creation**: OpenAI's DALL-E generates logo designs based on the user's brand description and color palette.
4. **Brand Similarity Search**: Pinecone is used to find and display similar brands based on vector similarity. This helps the user see what other brands in the same industry are doing.

### Features
- **Custom Logo Generation**: Automatically generate logos based on your brand's identity and industry using OpenAI's DALL-E.
- **Brand Kit Creation**: Get recommendations on color schemes, fonts, and taglines based on the personality and industry of your brand.
- **Brand Similarity Search**: Compare your brand with similar ones in the market using Pinecone's vector search.
- **Intuitive UI**: A clean, user-friendly interface built with Streamlit makes the process easy and interactive.

## Installation
1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/ai-brandkit.git
   cd brand-kit-generator

2. **Install dependencies**:

Install the required Python packages by running:
   ```bash
pip install -r requirements.txt


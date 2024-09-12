import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import json
import re
from sentence_transformers import SentenceTransformer
import openai
import anthropic
from pinecone import Pinecone

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MPNet-base-v2')

# Set your API keys
openai.api_key = "your-openai-api-key"
claude_api_key = "your-anthropic-api-key"
pinecone_api_key = "your-pinecone-api-key"

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=claude_api_key)

# Initialize the Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Connect to the existing Pinecone index
index_name = "brandkit"  # Replace with your Pinecone index name
index = pc.Index(index_name)

# Function to validate user input
def validate_input(user_input):
    required_fields = ["brand_name", "brand_description", "brand_industry", "company_keywords", "brand_personality", "target_segment"]
    for field in required_fields:
        if not user_input.get(field):
            st.write(f"Error: {field} is required")
            return False
    return True

# Function to query Pinecone for similar brands
def query_pinecone(user_input):
    input_text = f"{user_input['brand_name']} {user_input['brand_description']} {' '.join(user_input['company_keywords'])}"
    input_embedding = model.encode(input_text).tolist()

    results = index.query(
        vector=input_embedding,
        top_k=10,
        include_metadata=True
    )

    return results['matches']

# Function to combine user input with the matches from Pinecone
def combine_input_with_matches(user_input, matches):
    combined_text = (
        f"Brand Name: {user_input['brand_name']}. "
        f"Description: {user_input['brand_description']}. "
        f"Industry: {user_input['brand_industry']}. "
        f"Keywords: {', '.join(user_input['company_keywords'])}.\n\n"
        f"Similar Brands: \n"
    )
    if not matches:
        combined_text += "No similar brands found in Pinecone."
    else:
        for match in matches:
            metadata = match.get('metadata', {})
            combined_text += (
                f"- Brand Name: {metadata.get('brand_name', 'N/A')}, "
                f"Description: {metadata.get('brand_description', 'N/A')}, "
                f"Industry: {metadata.get('brand_industry', 'N/A')}, "
                f"Keywords: {metadata.get('company_keywords', 'N/A')}\n"
            )

    return combined_text

# Function to generate the brand kit based on user input and similar brands
def generate_brand_kit(combined_input):
    input_text = (
        f"The following is the description of a brand and its similar brands:\n\n"
        f"{combined_input}\n\n"
        "Based on the above information, provide the following in a structured format:\n"
        "1. **Color Theme**: Suggest 3-5 colors (in hex codes) suitable for the brand. Explain why each color was chosen.\n"
        "2. **Font Theme**: Suggest 2-3 fonts (for headings, body text, and accents).\n"
        "3. **Tagline**: Suggest a tagline that captures the essence of the brand.\n"
        "4. **Logo Concept**: Describe a logo concept aligned with the brand's industry and personality."
    )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            temperature=0.7,
            messages=[
                {"role": "user", "content": input_text}
            ]
        )

        generated_output = response.content[0].text.strip()
        return generated_output

    except Exception as e:
        st.write(f"An error occurred: {e}")
        return None

# Function to format Claude's output
def format_claude_output(output):
    # Split the output into sections
    sections = re.split(r'(\d+\.\s+\*\*[^*]+\*\*:)', output)
    
    formatted_output = ""
    for i in range(1, len(sections), 2):
        section_title = sections[i].strip()
        section_content = sections[i+1].strip()
        formatted_output += f"### {section_title}\n{section_content}\n\n"
    
    return formatted_output

# Function to generate logos using OpenAI DALL-E
def generate_logo(user_input, brand_kit_output):
    # Extract colors from the brand kit output
    colors = re.findall(r'#[0-9A-Fa-f]{6}', brand_kit_output)[:3]
    color_str = ', '.join(colors) if colors else 'vibrant colors'

    # Extract a brief concept from the logo concept section
    logo_concept_match = re.search(r'4\.\s+\*\*Logo Concept\*\*:(.*?)(?=\d+\.|\Z)', brand_kit_output, re.DOTALL)
    concept_summary = logo_concept_match.group(1).strip()[:100] + '...' if logo_concept_match else ''

    refined_prompt = (
        f"Design a modern, minimalist logo for a {user_input['brand_industry']} brand named {user_input['brand_name']}. "
        f"The logo should be tailored for {', '.join(user_input['company_keywords'][:3])} with a focus on {user_input['brand_personality']}. "
        f"Use these colors: {color_str}. "
        f"Do NOT include any text, brand name, or letters inside the logo. "
        f"Only use abstract shapes, icons, or symbols that represent the brand. "
        f"The logo should be a single symbol or icon (no text), no background. "
        f"Concept: {concept_summary}. "
        f"Strictly avoid including any text or letters inside the logo. Just a simple, memorable visual asset. "
        f"Ensure the logo is iconic, recognizable, and scalable for various branding needs."
    )

    image_urls = []

    for i in range(3):
        try:
            image_response = openai.Image.create(
                model="dall-e-3",
                prompt=refined_prompt,
                n=1,
                size="1024x1024"
            )
            image_urls.append(image_response['data'][0]['url'])
        except openai.error.OpenAIError as e:
            st.write(f"An error occurred generating logo {i+1}: {e}")

    return image_urls

# Function to display a logo from a URL
def display_logo(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    st.image(img, width=300)

# Streamlit app
def app():
    st.set_page_config(page_title="AI Brand Kit Generator", layout="centered")

    st.title("AI-Driven Brand Kit Generator")
    st.subheader("Craft a unique brand identity with AI.")
    st.write("Input your brand details, and our AI will generate a custom brand kit including colors, fonts, a tagline, and logos.")

    # Input Fields
    brand_name = st.text_input("Brand Name")  # No default value
    brand_description = st.text_area("Brand Description")  # No default value
    brand_industry = st.text_input("Brand Industry")  # No default value
    company_keywords = st.text_input("Company Keywords (comma-separated)")  # No default value
    brand_personality = st.selectbox("Brand Personality", ["Competence", "Excitement", "Sincerity", "Sophistication", "Ruggedness"])  # Dropdown options remain
    target_segment = st.text_input("Target Segment")  # No default value
    
    if st.button("Generate Brand Kit"):
        st.write("Generating your brand kit...")

        # Prepare user input
        user_input = {
            "brand_name": brand_name,
            "brand_description": brand_description,
            "brand_industry": brand_industry,
            "company_keywords": company_keywords.split(", "),
            "brand_personality": brand_personality,
            "target_segment": target_segment
        }

        if validate_input(user_input):
            # Query Pinecone to get similar brands
            matches = query_pinecone(user_input)

            # Combine user input with the matches from Pinecone
            combined_input = combine_input_with_matches(user_input, matches)

            # Generate the brand kit using the combined input
            generated_output = generate_brand_kit(combined_input)
            
            if generated_output:
                # Format Claude's output
                formatted_output = format_claude_output(generated_output)

                # Display the formatted output
                st.markdown("### Your Brand Kit")
                st.markdown(formatted_output)

                # Generate logos using the brand kit information
                image_urls = generate_logo(user_input, generated_output)

                # Display generated logos
                st.markdown("### Generated Logos")
                for i, url in enumerate(image_urls, 1):
                    st.write(f"Logo {i}")
                    display_logo(url)

if __name__ == "__main__":
    app()

!pip install sentence-transformers
!pip install pinecone-client
!pip install tensorflow

import pandas as pd
import pinecone
from sentence_transformers import SentenceTransformer
import json
import numpy as np

# Load the dataset with error handling for different encodings
file_path = "/content/company_info.csv"
try:
    df = pd.read_csv(file_path, encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv(file_path, encoding='latin-1')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='iso-8859-1')

# Initialize Pinecone
PINECONE_API_KEY = "your-pinecone-api-key"
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY, environment='us-west1-gcp')

# Connect to the existing index
index_name = "brandkit"
index = pinecone_client.Index(index_name)

# Define weights for each column (0 to 1)
weights = {
    "brand_tagline": 0.5,
    "brand_description": 1.0,
    "brand_mission": 0.5,
    "logo_description": 0.6,
    "brand_logo": 0.5,
    "brand_industry": 0.8,
    "brand_colors": 0.6,
    "brand_fonts": 0.5,
    "brand_personality": 0.5,
    "company_keywords": 0.9,
    "target_segment": 0.7
}

# Function to concatenate relevant columns into a single weighted text field
def concatenate_weighted_text(row):
    weighted_text = ""
    for col, weight in weights.items():
        text = str(row[col]) if pd.notna(row[col]) else ''
        weighted_text += (text + ' ') * int(weight * 10)  # Multiply the text based on the weight
    return weighted_text.strip()

# Create a combined weighted text field for embedding
df['combined_weighted_text'] = df.apply(concatenate_weighted_text, axis=1)

# Initialize the sentence transformer model
model = SentenceTransformer('all-MPNet-base-v2')

# Encode the text to get embeddings
embeddings = model.encode(df['combined_weighted_text'].tolist())

# Prepare the data for upsert
vector_data = []
for i, embedding in enumerate(embeddings):
    # Handle potential NaN values
    brand_tagline = df['brand_tagline'][i] if pd.notna(df['brand_tagline'][i]) else ''
    brand_description = df['brand_description'][i] if pd.notna(df['brand_description'][i]) else ''
    brand_mission = df['brand_mission'][i] if pd.notna(df['brand_mission'][i]) else ''
    logo_description = df['logo_description'][i] if pd.notna(df['logo_description'][i]) else ''
    brand_logo = df['brand_logo'][i] if pd.notna(df['brand_logo'][i]) else ''
    brand_industry = df['brand_industry'][i] if pd.notna(df['brand_industry'][i]) else ''
    brand_colors = json.dumps(df['brand_colors'][i]) if pd.notna(df['brand_colors'][i]) else ''
    brand_fonts = json.dumps(df['brand_fonts'][i]) if pd.notna(df['brand_fonts'][i]) else ''
    brand_personality = df['brand_personality'][i] if pd.notna(df['brand_personality'][i]) else ''
    company_keywords = json.dumps(df['company_keywords'][i]) if pd.notna(df['company_keywords'][i]) else ''
    target_segment = df['target_segment'][i] if pd.notna(df['target_segment'][i]) else ''

    metadata = {
        "brand_tagline": brand_tagline,
        "brand_description": brand_description,
        "brand_mission": brand_mission,
        "logo_description": logo_description,
        "brand_logo": brand_logo,
        "brand_industry": brand_industry,
        "brand_colors": brand_colors,
        "brand_fonts": brand_fonts,
        "brand_personality": brand_personality,
        "company_keywords": company_keywords,
        "target_segment": target_segment
    }

    vector_data.append((str(i), embedding.tolist(), metadata))

    # Print the metadata to debug
    print(f"Metadata for index {i}: {metadata}")

# Upsert the data in batches
batch_size = 100
for i in range(0, len(vector_data), batch_size):
    batch = vector_data[i:i+batch_size]
    index.upsert(vectors=batch)

print("Brand kit data uploaded to Pinecone successfully!")

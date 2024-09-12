from pyngrok import ngrok

# Use your ngrok auth token here
ngrok.set_auth_token("your-auth-token")

!streamlit run app.py &> /dev/null&

from pyngrok import ngrok

# Create a new ngrok tunnel to the Streamlit port (8501)
public_url = ngrok.connect(8501)
print(f"Public URL for the Streamlit app: {public_url}")


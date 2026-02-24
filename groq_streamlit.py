import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load env variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("Abhay GPT (Groq LLM)")

user_prompt = st.text_input("Enter your prompt:")

if st.button("Generate"):
    if not user_prompt:
        st.warning("Please enter the input!")
    else:
        try:
            with st.spinner("Generating response..."):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )

                st.success("Done!")
                st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error: {e}")
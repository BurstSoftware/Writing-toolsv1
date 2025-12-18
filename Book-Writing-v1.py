import streamlit as st
import google.generativeai as genai
import json

# -----------------------------------
# Page Config
# -----------------------------------
st.set_page_config(
    page_title="AI Book Chapter Writer",
    layout="wide"
)

st.title("📖 AI Book Chapter Writer")

# -----------------------------------
# Session State Initialization
# -----------------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "generated_output" not in st.session_state:
    st.session_state.generated_output = None

# -----------------------------------
# Sidebar – API Key Input
# -----------------------------------
with st.sidebar:
    st.header("🔑 Google AI Studio API Key")
    api_key = st.text_input(
        "Enter your Google API Key",
        type="password",
        value=st.session_state.api_key
    )
    st.session_state.api_key = api_key

    if not api_key:
        st.warning("Please enter your API key to continue.")

# -----------------------------------
# Main Input Form
# -----------------------------------
st.subheader("📚 Chapter Inputs")

with st.form("chapter_form"):
    col1, col2 = st.columns(2)

    with col1:
        book_name = st.text_input("Book Name")
        chapter_title = st.text_input("Chapter Title")
        narrative_style = st.text_area(
            "Narrative Style",
            placeholder="e.g. First-person, poetic, dark fantasy..."
        )

    with col2:
        sequence = st.text_area(
            "Chapter Sequence / Outline",
            placeholder="Describe the flow of the chapter..."
        )
        details = st.text_area(
            "Additional Details / Constraints",
            placeholder="Themes, tone, pacing, word count, etc."
        )

    submitted = st.form_submit_button("✍️ Generate Chapter")

# -----------------------------------
# Gemini Generation
# -----------------------------------
if submitted:
    if not api_key:
        st.error("API key is required.")
    else:
        try:
            genai.configure(api_key=api_key)

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.8,
                    "response_mime_type": "application/json"
                }
            )

            prompt = f"""
You are a professional book author.

Write a chapter using the following structured inputs:

Book Name: {book_name}
Chapter Title: {chapter_title}
Narrative Style: {narrative_style}
Chapter Sequence: {sequence}
Additional Details: {details}

Return your response in JSON with the following structure:
{{
  "book_name": "",
  "chapter_title": "",
  "narrative_style": "",
  "chapter_summary": "",
  "chapter_content": ""
}}
"""

            with st.spinner("Generating chapter..."):
                response = model.generate_content(prompt)

            output_text = response.text

            # Attempt to parse JSON
            try:
                structured_output = json.loads(output_text)
            except json.JSONDecodeError:
                structured_output = {"raw_output": output_text}

            st.session_state.generated_output = structured_output

        except Exception as e:
            st.error(f"Error: {e}")

# -----------------------------------
# Output Display
# -----------------------------------
if st.session_state.generated_output:
    st.subheader("🧠 Generated Output")

    if "chapter_content" in st.session_state.generated_output:
        st.markdown(f"### {st.session_state.generated_output['chapter_title']}")
        st.write(st.session_state.generated_output["chapter_content"])

        with st.expander("📦 Structured JSON Output"):
            st.json(st.session_state.generated_output)
    else:
        st.warning("Could not parse structured output.")
        st.write(st.session_state.generated_output)

import streamlit as st
from snowflake.snowpark.context import get_active_session
import os

# Setup
stage_path = "@ml_models.ds.image_files"
session = get_active_session()

# Initialize session_state for dropdowns
if "model_selected" not in st.session_state:
    st.session_state.model_selected = "claude-3-5-sonnet"

if "Filename" not in st.session_state:
    # Query stage files only once
    query = f"SELECT * FROM DIRECTORY({stage_path})"
    results = session.sql(query).collect()
    st.session_state.dropdown_options = [row[0] for row in results]
    st.session_state.Filename = st.session_state.dropdown_options[0]  # default to first

# Sidebar - Choose model (independent)
model = st.sidebar.selectbox("Choose model:", ["claude-3-5-sonnet", "pixtral-large"],
                             index=["claude-3-5-sonnet", "pixtral-large"].index(st.session_state.model_selected))
st.session_state.model_selected = model

# Sidebar - Choose image (independent)
Filename = st.sidebar.selectbox("Choose image file to load:", st.session_state.dropdown_options,
                                index=st.session_state.dropdown_options.index(st.session_state.Filename))
st.session_state.Filename = Filename
st.sidebar.write(f"You selected file: **{Filename}**")

# --- Load image from Snowflake stage ---
def load_image_from_stage(stage_path, filename):
    full_path = stage_path + '/' + filename
    try:
        download_dir = f"/tmp/image_download/{filename}"
        os.makedirs(os.path.dirname(download_dir), exist_ok=True)

        if os.path.exists(download_dir):
            os.remove(download_dir)

        session.file.get(full_path, os.path.dirname(download_dir))

        if not os.path.exists(download_dir):
            raise FileNotFoundError(f"File not found at {download_dir}")

        with open(download_dir, "rb") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# --- Call Cortex with image + question ---
def image_llm(user_question, filename, model_selected):
    sql_text = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        '{model_selected}',
        '{user_question}',
        TO_FILE('{stage_path}', '{filename}')
    ) AS response;
    """
    try:
        result_df = session.sql(sql_text).to_pandas()
        if not result_df.empty:
            st.success("LLM Response:")
            st.write(result_df["RESPONSE"].iloc[0])
        else:
            st.warning("No response returned.")
    except Exception as e:
        st.error(f"Error executing query: {e}")

# App title
st.title("Ask Cortex about Insight from the uploaded Image")

# Display the image
image_bytes = load_image_from_stage(stage_path, st.session_state.Filename)
if image_bytes:
    st.image(image_bytes, caption=f"Image: {st.session_state.Filename}", use_container_width=True)

# Question input
if "user_question" not in st.session_state:
    st.session_state.user_question = ""

st.subheader("Ask a question about the image:")
user_input = st.text_input("Your question here:", value=st.session_state.user_question, key="question_input")

if st.button("Submit"):
    st.session_state.user_question = user_input
    if user_input:
        with st.spinner("⏳ Waiting for LLM to respond..."):
            image_llm(user_input, st.session_state.Filename, st.session_state.model_selected)

# Clear question
if st.sidebar.button("Clear"):
    st.session_state.user_question = ""
    st.sidebar.info("Question cleared. You can now type a new one.")

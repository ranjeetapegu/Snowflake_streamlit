import streamlit as st
from snowflake.snowpark.context import get_active_session
import os

stage_path = "@ml_models.ds.image_files"
session = get_active_session()


model_selected = st.sidebar.selectbox("Choose model:", ["claude-3-5-sonnet", "pixtral-large"])

# Query stage files for dropdown
query = f"SELECT * FROM DIRECTORY({stage_path})"
results = session.sql(query).collect()
dropdown_options = [row[0] for row in results]

# Sidebar dropdown
Filename = st.sidebar.selectbox("Choose image file to load:", dropdown_options)
st.sidebar.write(f"You selected file: **{Filename}**")

# --- Function to load image from Snowflake stage ---
def load_image_from_stage(stage_path, filename):
    full_path = stage_path + '/' + filename
    try:
        st.write("Downloading image from Snowflake stage...")
        download_dir = "/tmp/image_download"
        os.makedirs(download_dir, exist_ok=True)
        session.file.get(full_path, download_dir)
        files = os.listdir(download_dir)
        if not files:
            raise FileNotFoundError("No file found in the download directory.")
        local_file_path = os.path.join(download_dir, files[0])
        with open(local_file_path, "rb") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# --- Function to call Cortex with image and question ---
def image_llm(user_question, filename,model_selected):
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

# App Layout
st.title("Ask Cortex about Insight from the uploaded Image")

image_bytes = load_image_from_stage(stage_path, Filename)
if image_bytes:
    st.image(image_bytes, caption=f"Image: {Filename}", use_container_width=True)

# Question input
st.markdown("### ")
if "user_question" not in st.session_state:
    st.session_state.user_question = ""

st.subheader("Ask a question about the image:")
user_input = st.text_input("Your question here:", value=st.session_state.user_question, key="question_input")

if st.button("Submit"):
    st.session_state.user_question = user_input
    if user_input:
        image_llm(user_input, Filename,model_selected)

if st.sidebar.button("Clear"):
    st.session_state.user_question = ""
    st.sidebar.info("Question cleared. You can now type a new one.")

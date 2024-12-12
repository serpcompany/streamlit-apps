import os
import requests
import pandas as pd
import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile
import tempfile
import base64
import streamlit.components.v1 as components

# Function to read prompts from a CSV file
def read_prompts_from_csv(uploaded_file):
    csv_data = pd.read_csv(uploaded_file)
    prompts = [
        {
            "prompt": row["prompt"],
            "num_images": int(row["num_images"]),
            "keyword": row["keyword"],
        }
        for _, row in csv_data.iterrows()
    ]
    return prompts


# Function to generate DALL-E images with progress indicator and incremental saving
def generate_dalle_images(prompts, api_key, progress_bar, progress_text, temp_zip_path):
    headers = {"Authorization": f"Bearer {api_key}"}
    total_tasks = sum(prompt["num_images"] for prompt in prompts)
    completed_tasks = 0

    with zipfile.ZipFile(temp_zip_path, "w") as zip_file:
        for prompt_details in prompts:
            prompt = prompt_details["prompt"]
            num_images = prompt_details["num_images"]
            keyword = prompt_details["keyword"]

            for i in range(num_images):
                data = {
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1792x1024",
                    "quality": "hd",
                }

                response = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=data,
                )

                if response.status_code == 200:
                    images = response.json()["data"]
                    for img in images:
                        image_response = requests.get(img["url"])
                        if image_response.status_code == 200:
                            image = Image.open(BytesIO(image_response.content))
                            image_file_name = f"{keyword.replace(' ', '_')}_{i + 1}.png"
                            img_buffer = BytesIO()
                            image.save(img_buffer, format="PNG")
                            zip_file.writestr(image_file_name, img_buffer.getvalue())
                        else:
                            st.error(f"Error loading image: {image_response.status_code}")
                else:
                    error_message = response.json().get("error", {}).get("message", "Unknown error")
                    st.error(f"Error: {response.status_code} - {error_message}")
                    return  # Stop further processing on error

                # Update progress
                completed_tasks += 1
                progress = completed_tasks / total_tasks
                progress_bar.progress(progress)
                progress_text.text(f"Generating images... {completed_tasks}/{total_tasks} completed.")


# Initialize session state for ZIP file path
if "zip_file_path" not in st.session_state:
    st.session_state.zip_file_path = None
if "auto_download" not in st.session_state:
    st.session_state.auto_download = False

# ------------------------------
# Streamlit UI
st.set_page_config(layout="wide", page_title="SERP AI: DALL-E Bulk Image Generator")
st.title("DALL-E Bulk Image Generator")
st.subheader("By SERP")

# ------------------------------
# HERO AREA
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    components.html(
        """
        <iframe width="100%" height="315" src="https://www.youtube.com/embed/zfc7Exry20o" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        """,
        height=315,
    )

with col2:
    st.markdown(
        """
        ### Questions?

        - [Join Discord](https://serp.ly/@serp/discord)
        - [SERP](https://serp.co)
        - [SERP AI](https://serp.ai)
        - [DevinSchumacher.com](https://devinschumacher.com)
        - [YouTube Tutorials](https://serp.ly/@devin/youtube)
        """
    )

with col3:
    st.markdown(
        """
        ### Support Free AI Tools
        - [Sponsor @devinschumacher](https://serp.ly/@devinschumacher/sponsor)
        ---
        """
    )

# END HERO AREA
# ------------------------------

api_key = st.text_input("Step 1: Enter your OpenAI API Key:", type="password")
uploaded_file = st.file_uploader("Step 2: Upload a CSV file with column headers: `prompt`, `num_images`, `keyword`", type="csv")

# Generate Images Button
if st.button("Generate Images"):
    if uploaded_file and api_key:
        prompts = read_prompts_from_csv(uploaded_file)
        temp_zip_path = os.path.join(tempfile.gettempdir(), "generated_images.zip")
        st.session_state.zip_file_path = temp_zip_path  # Save the ZIP file path in session state

        with st.spinner("Starting image generation..."):
            # Add progress bar and progress text
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            # Generate images and save incrementally to ZIP file
            generate_dalle_images(prompts, api_key, progress_bar, progress_text, temp_zip_path)
        
        st.success("Image generation completed!")
        st.session_state.auto_download = True  # Trigger auto-download

# Persistent Download Button
if st.session_state.zip_file_path:
    with open(st.session_state.zip_file_path, "rb") as zip_file:
        st.download_button(
            label="Download All Images as ZIP",
            data=zip_file,
            file_name="generated_images.zip",
            mime="application/zip",
        )

# Automatically trigger download
if st.session_state.auto_download:
    with open(st.session_state.zip_file_path, "rb") as file:
        zip_content = base64.b64encode(file.read()).decode()
        href = f'data:application/zip;base64,{zip_content}'
        st.markdown(
            f"""
            <script>
                var link = document.createElement('a');
                link.href = '{href}';
                link.download = 'generated_images.zip';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            </script>
            """,
            unsafe_allow_html=True,
        )
    st.session_state.auto_download = False  # Prevent repeated triggers

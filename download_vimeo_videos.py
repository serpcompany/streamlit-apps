import os
import subprocess

try:
    import streamlit as st
    import streamlit.components.v1 as components
except ModuleNotFoundError:
    raise ModuleNotFoundError("The 'streamlit' module is not installed. Please install it using 'pip install streamlit' and try again.")

def extract_vimeo_id(vimeo_url: str) -> str:
    """Extract the Vimeo video ID from the full URL.

    Args:
        vimeo_url (str): The full Vimeo video URL.

    Returns:
        str: Extracted Vimeo video ID.
    """
    try:
        return vimeo_url.strip().split("/")[-1]
    except IndexError:
        raise ValueError("Invalid Vimeo URL format.")

def download_vimeo_video(vimeo_id: str):
    """Download a Vimeo video using Streamlink to the user's desktop.

    Args:
        vimeo_id (str): The Vimeo video ID.

    Returns:
        str: Success or error message.
    """
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_path = os.path.join(desktop_path, f"vimeo_video_{vimeo_id}.mp4")
    vimeo_url = f"https://player.vimeo.com/video/{vimeo_id}"
    command = [
        "streamlink",
        vimeo_url,
        "best",
        "-o",
        output_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Video downloaded successfully to {output_path}"
        else:
            return f"Error: {result.stderr.strip()}"
    except FileNotFoundError:
        return "Streamlink is not installed or not found in the system PATH. Please install it and try again."
    except Exception as e:
        return f"An exception occurred: {str(e)}"


# HERO AREA
# Streamlit App
st.set_page_config(
    layout="wide", 
    page_title="Vimeo Video Downloader",
)
st.title("Free Vimeo Video Downloader")
st.subheader("By SERP")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    components.html(
        """
        <iframe width="100%" height="315" src="https://www.youtube.com/embed/MeLNJSwCnwk" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
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
        ### Support Free Tools
        - [Sponsor @devinschumacher](https://serp.ly/@devinschumacher/sponsor)
        ---
        """
    )
# END HERO AREA

vimeo_url = st.text_input("Enter Vimeo Video PLAYER URL - example: https://player.vimeo.com/video/783022286")

if st.button("Download Video"):
    if vimeo_url:
        try:
            vimeo_id = extract_vimeo_id(vimeo_url)
            with st.spinner("Downloading video..."):
                message = download_vimeo_video(vimeo_id)
            if "successfully" in message:
                st.success(message)
            else:
                st.error(message)
        except ValueError as e:
            st.error(str(e))
    else:
        st.error("Please provide the Vimeo Video URL.")

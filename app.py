import streamlit as st
import requests
import re

st.set_page_config(page_title="Pro Media Downloader", page_icon="⚡", layout="wide")

# Modern UI Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput input { background-color: #1e1e1e; color: white; border: 1px solid #ff4b4b; }
    .stButton button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; height: 3em; }
    .stButton button:hover { background-color: #ff3333; border: none; }
    .download-card { background-color: #1e1e1e; padding: 20px; border-radius: 15px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Pro Media Downloader")
st.write("Fast, high-quality downloads without 'Bot' errors. Powered by Cobalt.")

url = st.text_input("", placeholder="Paste YouTube, TikTok, or Instagram URL here...")

if url:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("🎯 **Step 1: Select Format**")
        mode = st.radio("What do you want to download?", ["Video (High Quality)", "Audio (MP3)"])
        
    with col2:
        st.info("⚙️ **Step 2: Process**")
        if st.button("Generate Download Link"):
            # We use a public Cobalt instance API
            # This handles the bot bypass for us!
            api_url = "https://api.cobalt.tools/api/json"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": url,
                "videoQuality": "1080", # Max quality
                "downloadMode": "audio" if mode == "Audio (MP3)" else "video",
                "filenameStyle": "pretty"
            }
            
            try:
                with st.spinner("Bypassing YouTube security..."):
                    response = requests.post(api_url, json=payload, headers=headers)
                    result = response.json()
                
                if result.get("status") == "stream" or result.get("status") == "redirect":
                    download_link = result.get("url")
                    
                    st.markdown(f"""
                    <div class="download-card">
                        <h3>✅ Success! Your file is ready.</h3>
                        <p>Cobalt has bypassed the security. Click the button below to save the file.</p>
                        <a href="{download_link}" target="_blank">
                            <button style="width:100%; padding:15px; background-color:#00cc66; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">
                                📥 DOWNLOAD NOW
                            </button>
                        </a>
                        <p style="font-size: 0.8em; color: #888; margin-top:10px;">Note: If the video plays in browser, right-click and 'Save Video As'.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Error: {result.get('text', 'Could not process this link.')}")
                    
            except Exception as e:
                st.error("The Cobalt service is currently busy. Please try again in a moment.")

st.markdown("---")
st.caption("Supports: YouTube, Twitter, TikTok, Instagram, and more.")

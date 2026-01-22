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
    .download-card { background-color: #1e1e1e; padding: 25px; border-radius: 15px; border-left: 5px solid #00cc66; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Pro Media Downloader")
st.write("Fast, high-quality downloads using Cobalt Fallback System.")

# List of multiple Cobalt API instances (If one is slow, the app tries the next)
COBALT_INSTANCES = [
    "https://api.cobalt.tools/api/json",
    "https://co.wuk.sh/api/json",
    "https://cobalt.hypert.lol/api/json"
]

url = st.text_input("", placeholder="Paste YouTube, TikTok, or Instagram URL here...")

if url:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("🎯 **Step 1: Select Format**")
        mode = st.radio("What do you want to download?", ["Video (1080p/Best)", "Audio (MP3)"])
        
    with col2:
        st.info("⚙️ **Step 2: Process**")
        if st.button("Generate Download Link"):
            success = False
            
            # TRY EACH SERVER UNTIL ONE WORKS
            for i, api_url in enumerate(COBALT_INSTANCES):
                try:
                    with st.spinner(f"Trying Server {i+1}..."):
                        payload = {
                            "url": url,
                            "videoQuality": "1080",
                            "downloadMode": "audio" if mode == "Audio (MP3)" else "video",
                            "filenameStyle": "pretty"
                        }
                        
                        # Added a 15-second timeout so it doesn't hang forever
                        response = requests.post(
                            api_url, 
                            json=payload, 
                            headers={"Accept": "application/json", "Content-Type": "application/json"},
                            timeout=15 
                        )
                        result = response.json()
                    
                    if result.get("status") in ["stream", "redirect"]:
                        download_link = result.get("url")
                        st.markdown(f"""
                        <div class="download-card">
                            <h3 style="color:#00cc66;">✅ File Ready! (Server {i+1})</h3>
                            <p>Security bypassed. Download will start instantly.</p>
                            <a href="{download_link}" target="_blank">
                                <button style="width:100%; padding:15px; background-color:#00cc66; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:1.2em;">
                                    📥 DOWNLOAD FILE NOW
                                </button>
                            </a>
                            <p style="font-size: 0.8em; color: #888; margin-top:10px;">If it plays in browser instead of downloading: <b>Right Click > Save Video As</b>.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        success = True
                        break # Stop trying other servers once we win
                
                except Exception:
                    continue # Try the next server in the list
            
            if not success:
                st.error("❌ All download servers are currently busy or blocked by YouTube. Please try again in 5 minutes.")

st.markdown("---")
st.caption("No ads. No tracking. Pure speed.")

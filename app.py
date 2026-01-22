import streamlit as st
import requests
import re
import time

st.set_page_config(page_title="Pro Downloader", page_icon="🎬", layout="wide")

# Professional Dark UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput input { background-color: #1e1e1e; color: white; border: 1px solid #3d5afe; }
    .stButton button { width: 100%; background-color: #3d5afe; color: white; font-weight: bold; border-radius: 8px; height: 3.5em; border: none; }
    .stButton button:hover { background-color: #536dfe; border: none; color: white; }
    .status-box { padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #3d5afe; background-color: #1e1e1e; }
    .success-card { background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 2px solid #00c853; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Multi-Platform Pro Downloader")
st.write("If one server fails, we automatically try another. Works for YouTube, TikTok, IG, and Twitter.")

# THE MIRROR LIST (7 Global Instances)
# We use these because YouTube blocks individual IPs frequently.
COBALT_MIRRORS = [
    "https://api.cobalt.tools/api/json",
    "https://cobalt.moe/api/json",
    "https://cobalt-api.v06.re/api/json",
    "https://api.wuk.sh/api/json",
    "https://co.wuk.sh/api/json",
    "https://cobalt.fastest.sh/api/json",
    "https://cobalt.sh/api/json"
]

url = st.text_input("", placeholder="Paste your link here (YouTube, TikTok, Instagram...)", label_visibility="collapsed")

if url:
    c1, c2 = st.columns(2)
    with c1:
        quality = st.select_slider("Select Video Quality", options=["360", "480", "720", "1080"], value="1080")
    with c2:
        mode = st.selectbox("Download Mode", ["Video + Audio", "Audio Only (MP3)"])

    if st.button("🔍 FIND DOWNLOAD LINK"):
        success = False
        progress_text = st.empty()
        
        # Loop through all mirrors
        for i, mirror in enumerate(COBALT_MIRRORS):
            try:
                progress_text.markdown(f"<div class='status-box'>📡 Trying Server {i+1} of {len(COBALT_MIRRORS)}...</div>", unsafe_allow_html=True)
                
                payload = {
                    "url": url,
                    "videoQuality": quality,
                    "downloadMode": "audio" if "Audio" in mode else "video",
                    "filenameStyle": "pretty",
                    "youtubeVideoCodec": "h264" # Most compatible for iPhones/Windows
                }
                
                # We give each server 10 seconds to respond
                response = requests.post(
                    mirror, 
                    json=payload, 
                    headers={"Accept": "application/json", "Content-Type": "application/json"},
                    timeout=10
                )
                
                data = response.json()
                
                if data.get("status") in ["stream", "redirect"]:
                    final_url = data.get("url")
                    progress_text.empty()
                    
                    st.markdown(f"""
                    <div class="success-card">
                        <h2 style="color:#00c853;">🎉 Success! Server {i+1} Worked</h2>
                        <p>Your download is ready. Click the button below.</p>
                        <a href="{final_url}" target="_blank">
                            <button style="width:100%; padding:15px; background-color:#00c853; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:1.2em;">
                                📥 SAVE FILE TO DEVICE
                            </button>
                        </a>
                        <p style="font-size: 0.8em; color: #888; margin-top:10px;">
                            If it plays in the browser, <b>Right-Click</b> and select <b>'Save Video As'</b>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    success = True
                    break
                
                elif data.get("status") == "error":
                    # If server returns error, we move to the next one
                    continue

            except Exception:
                # If server times out or crashes, we move to the next one
                continue
        
        if not success:
            progress_text.empty()
            st.error("❌ YouTube is currently blocking all our cloud servers. This usually lasts for 15-30 minutes. Please try again later or try a different video.")
            st.info("💡 **Tip:** YouTube sometimes blocks high-quality (1080p) requests from cloud servers. Try selecting **720p** or **Audio Only** to see if it works.")

st.markdown("---")
st.caption("Powered by the Global Cobalt Network.")

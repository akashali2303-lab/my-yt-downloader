import streamlit as st
import requests
import re

st.set_page_config(page_title="Universal Downloader", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; height: 3.5em; }
    .download-card { background-color: #1e1e1e; padding: 20px; border-radius: 15px; border-left: 5px solid #00cc66; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Universal Pro Downloader")
st.write("Bypassing YouTube blocks using Hybrid Proxy Logic.")

# List of backup engines
COBALT_URLS = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]
INVIDIOUS_INSTANCES = [
    "https://invidious.flokinet.to",
    "https://yewtu.be",
    "https://inv.tux.rs",
    "https://invidious.nerdvpn.de"
]

url = st.text_input("", placeholder="Paste your link here...")

if url:
    mode = st.radio("Format:", ["Video (MP4)", "Audio (MP3)"], horizontal=True)
    
    if st.button("🚀 GENERATE DOWNLOAD LINK"):
        success = False
        status = st.empty()

        # --- PHASE 1: TRY COBALT (High Quality 1080p) ---
        status.info("📡 Phase 1: Contacting Global Download Nodes...")
        for api in COBALT_URLS:
            try:
                payload = {
                    "url": url,
                    "videoQuality": "720", # 720 is more stable than 1080 for cloud bypass
                    "downloadMode": "audio" if "Audio" in mode else "video",
                    "filenameStyle": "pretty",
                    "youtubeVideoCodec": "h264"
                }
                res = requests.post(api, json=payload, headers={"Accept": "application/json"}, timeout=8)
                data = res.json()
                if data.get("status") in ["stream", "redirect"]:
                    dl_link = data.get("url")
                    st.balloons()
                    st.markdown(f"""
                    <div class="download-card">
                        <h3 style="color:#00cc66;">✅ High-Speed Link Ready</h3>
                        <a href="{dl_link}" target="_blank">
                            <button style="width:100%; padding:15px; background-color:#00cc66; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">
                                📥 DOWNLOAD NOW
                            </button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    success = True
                    break
            except:
                continue

        # --- PHASE 2: TRY INVIDIOUS PROXY (The Ultimate Backup) ---
        if not success:
            status.info("📡 Phase 2: Cobalt blocked. Switching to Invidious Proxies...")
            video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
            if video_id_match:
                vid = video_id_match.group(1)
                for instance in INVIDIOUS_INSTANCES:
                    try:
                        # We look for direct video streams from Invidious
                        api_url = f"{instance}/api/v1/videos/{vid}"
                        res = requests.get(api_url, timeout=5)
                        data = res.json()
                        # Get the first available MP4 stream
                        streams = data.get("formatStreams", [])
                        if streams:
                            dl_link = streams[-1].get("url") # Take highest quality available
                            status.empty()
                            st.markdown(f"""
                            <div class="download-card" style="border-left-color: #ffcc00;">
                                <h3 style="color:#ffcc00;">⚠️ Standard Quality Link Ready</h3>
                                <p>YouTube blocked high-speed servers. This is a secure backup link.</p>
                                <a href="{dl_link}" target="_blank">
                                    <button style="width:100%; padding:15px; background-color:#ffcc00; color:black; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">
                                        📥 DOWNLOAD FROM PROXY
                                    </button>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                            success = True
                            break
                    except:
                        continue

        if not success:
            status.empty()
            st.error("❌ Deep Block: YouTube is currently blocking all known cloud bypasses for this video. Please try again in 1 hour or try a different video.")
            st.info("💡 **Pro Tip:** Try a **TikTok** or **Twitter** link; they almost never get blocked!")

st.markdown("---")
st.caption("Anti-Block Engine v4.0 (Hybrid Cobalt/Invidious)")

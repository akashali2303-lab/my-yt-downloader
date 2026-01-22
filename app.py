import streamlit as st
import yt_dlp
import os
import re

st.set_page_config(page_title="Ultimate Downloader", page_icon="🎬", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stDownloadButton button {
        background-color: #00cc66 !important;
        color: white !important;
        font-weight: bold !important;
        height: 3em !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Ultimate YouTube Downloader")
url = st.text_input("Paste YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%').replace('%','')
        try:
            progress_bar.progress(float(p)/100)
            status_text.text(f"📥 STEP 1: Server is grabbing file... {d.get('_percent_str')} | Speed: {d.get('_speed_str')}")
        except:
            pass

if url:
    try:
        # ADVANCED BYPASS: Switching to Android/TV clients which rarely ask for "Sign in"
        ydl_opts_base = {
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'no_warnings': True,
            # This is the magic part: it forces yt-dlp to use clients that don't trigger the "Bot" check easily
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_test', 'web_embedded'],
                    'po_token': ['web+QUFE...'] # Fake token structure hint
                }
            }
        }

        with st.spinner("🔍 Analyzing Video (Bypassing Bot Check)..."):
            with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                formats = info.get('formats', [])
                thumbnail = info.get('thumbnail')

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(thumbnail, use_container_width=True)
        with col2:
            st.subheader(video_title)
            tab_video, tab_audio = st.tabs(["📺 Video Formats", "🎵 Audio Only (MP3)"])

            with tab_video:
                video_options = []
                for f in formats:
                    if f.get('vcodec') != 'none':
                        res = f.get('resolution') or f"{f.get('height')}p"
                        size_bytes = f.get('filesize') or f.get('filesize_approx')
                        size_mb = f"{size_bytes/(1024*1024):.1f} MB" if size_bytes else "Variable Size"
                        label = f"{res} - {size_mb} ({f.get('ext')})"
                        video_options.append({"label": label, "id": f.get('format_id'), "res_val": f.get('height') or 0})
                
                video_options = list({v['label']: v for v in video_options}.values())
                video_options.sort(key=lambda x: x['res_val'], reverse=True)
                
                if video_options:
                    selected_video = st.selectbox("Select Video Quality:", video_options, format_func=lambda x: x['label'])
                    btn_video = st.button("🚀 Step 1: Prepare Video")
                else:
                    st.warning("No video formats found.")
                    btn_video = False

            with tab_audio:
                audio_options = [
                    {"label": "High Quality (320kbps)", "id": "bestaudio/best", "abr": 320},
                    {"label": "Medium Quality (128kbps)", "id": "bestaudio/best", "abr": 128},
                ]
                selected_audio = st.selectbox("Select Audio Quality:", audio_options, format_func=lambda x: x['label'])
                btn_audio = st.button("🎵 Step 1: Prepare MP3")

        if btn_video or btn_audio:
            safe_title = re.sub(r'[^\w\s-]', '', video_title).strip()
            status_text = st.empty()
            progress_bar = st.progress(0)

            if btn_video:
                final_filename = f"{safe_title}.mp4"
                dl_format = f"{selected_video['id']}+bestaudio/best"
                post_p = []
            else:
                final_filename = f"{safe_title}.mp3"
                dl_format = selected_audio['id']
                post_p = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': str(selected_audio['abr'])}]

            dl_opts = {
                **ydl_opts_base,
                'format': dl_format,
                'outtmpl': f"temp_file_%(id)s.%(ext)s",
                'progress_hooks': [progress_hook],
                'postprocessors': post_p,
                'merge_output_format': 'mp4' if btn_video else None,
            }

            try:
                with yt_dlp.YoutubeDL(dl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info_dict)
                    
                    if btn_audio:
                        file_path = file_path.rsplit('.', 1)[0] + ".mp3"
                    elif btn_video:
                        file_path = file_path.rsplit('.', 1)[0] + ".mp4"

                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        status_text.empty()
                        progress_bar.empty()
                        st.balloons()
                        st.success("✨ STEP 2: File is Ready!")
                        st.download_button(
                            label=f"💾 CLICK HERE TO SAVE: {final_filename}",
                            data=f,
                            file_name=final_filename,
                            mime="video/mp4" if btn_video else "audio/mpeg"
                        )
                    # Clean up
                    os.remove(file_path)
                else:
                    st.error("Error: The server finished but the file was not found.")

            except Exception as e:
                st.error(f"Download Error: {e}")

    except Exception as e:
        st.error(f"Analysis Error: YouTube is currently blocking the server. Try a different video or wait 10 minutes.")

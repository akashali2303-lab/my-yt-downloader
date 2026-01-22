import streamlit as st
import yt_dlp
import os
import re

st.set_page_config(page_title="Ultimate Downloader", page_icon="🎬", layout="wide")

st.title("🎬 Ultimate YouTube Downloader")
st.markdown("Choose between **Video (with sound)** or **Audio (MP3)** formats.")

url = st.text_input("Paste YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%').replace('%','')
        try:
            progress_bar.progress(float(p)/100)
            status_text.text(f"Server is downloading: {d.get('_percent_str')} | Speed: {d.get('_speed_str')} | ETA: {d.get('_eta_str')}s")
        except:
            pass

if url:
    try:
        with st.spinner("Fetching available formats..."):
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                formats = info.get('formats', [])
                thumbnail = info.get('thumbnail')

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(thumbnail, use_container_width=True)
        with col2:
            st.subheader(video_title)
            
            # Create Tabs for Video and Audio
            tab_video, tab_audio = st.tabs(["📺 Video Formats", "🎵 Audio Only (MP3)"])

            with tab_video:
                video_options = []
                for f in formats:
                    # Filter for video streams
                    if f.get('vcodec') != 'none':
                        res = f.get('resolution') or f"{f.get('height')}p"
                        ext = f.get('ext')
                        fid = f.get('format_id')
                        
                        # Size calculation
                        size_bytes = f.get('filesize') or f.get('filesize_approx')
                        size_mb = f"{size_bytes/(1024*1024):.1f} MB" if size_bytes else "Size Varies"
                        
                        video_options.append({
                            "label": f"{res} (.{ext}) - {size_mb}",
                            "id": fid,
                            "ext": ext
                        })
                
                # Show unique resolutions (highest first)
                video_options = list({v['label']: v for v in video_options}.values())
                video_options.sort(key=lambda x: int(re.sub(r'\D', '', x['label'].split(' ')[0]) or 0), reverse=True)
                
                selected_video = st.selectbox("Select Video Quality:", video_options, format_func=lambda x: x['label'], key="v_sel")
                btn_video = st.button("🚀 Prepare Video Download")

            with tab_audio:
                audio_options = [
                    {"label": "High Quality (320kbps)", "id": "bestaudio/best", "abr": 320},
                    {"label": "Medium Quality (128kbps)", "id": "bestaudio/best", "abr": 128},
                    {"label": "Low Quality (64kbps)", "id": "bestaudio/best", "abr": 64},
                ]
                selected_audio = st.selectbox("Select Audio Quality:", audio_options, format_func=lambda x: x['label'], key="a_sel")
                btn_audio = st.button("🎵 Prepare MP3 Download")

        # --- DOWNLOAD LOGIC ---
        if btn_video or btn_audio:
            safe_title = re.sub(r'[^\w\s-]', '', video_title).strip()
            status_text = st.empty()
            progress_bar = st.progress(0)

            if btn_video:
                # Video Logic: Combine selected video + best audio
                output_ext = "mp4"
                download_format = f"{selected_video['id']}+bestaudio/best"
                final_filename = f"{safe_title}.mp4"
                post_processors = []
            else:
                # Audio Logic: Convert to MP3
                output_ext = "mp3"
                download_format = selected_audio['id']
                final_filename = f"{safe_title}.mp3"
                post_processors = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': str(selected_audio['abr']),
                }]

            dl_opts = {
                'format': download_format,
                'outtmpl': f"temp_file.%(ext)s",
                'progress_hooks': [progress_hook],
                'postprocessors': post_processors,
                'merge_output_format': 'mp4' if btn_video else None,
                'quiet': True
            }

            try:
                with yt_dlp.YoutubeDL(dl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    downloaded_file = ydl.prepare_filename(info_dict)
                    
                    # Handle the extension change after MP3 conversion
                    if btn_audio:
                        downloaded_file = downloaded_file.rsplit('.', 1)[0] + ".mp3"

                with open(downloaded_file, "rb") as f:
                    st.success("✅ Ready!")
                    st.download_button(
                        label="💾 Download File to Computer",
                        data=f,
                        file_name=final_filename,
                        mime="video/mp4" if btn_video else "audio/mpeg",
                        use_container_width=True
                    )
                
                # Cleanup server files
                if os.path.exists(downloaded_file): os.remove(downloaded_file)
                if os.path.exists("temp_file.mp4"): os.remove("temp_file.mp4")

            except Exception as e:
                st.error(f"Error: {e}")

    except Exception as e:
        st.error(f"Analysis Error: {e}")

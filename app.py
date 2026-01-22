import streamlit as st
import yt_dlp
import os
import re

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬")

st.title("🎬 YouTube All-Format Downloader")
st.markdown("Download high-quality videos for free.")

url = st.text_input("Paste YouTube URL here:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        with st.spinner("Analyzing video..."):
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                video_thumb = info.get('thumbnail')
                
                # Filter formats to show only those with both video and audio
                # and clean the list for the user
                formats = info.get('formats', [])
                
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(video_thumb)
        with col2:
            st.subheader(video_title)
            st.write(f"**Duration:** {info.get('duration_string')}")

        # Selection for quality
        # We focus on the best quality combinations
        display_formats = []
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                res = f.get('resolution')
                ext = f.get('ext')
                fid = f.get('format_id')
                filesize = f.get('filesize') or f.get('filesize_approx')
                size_mb = f"{filesize/(1024*1024):.1f} MB" if filesize else "Unknown size"
                display_formats.append({
                    "label": f"{res} ({ext}) - {size_mb}",
                    "id": fid,
                    "ext": ext
                })

        if display_formats:
            selected_option = st.selectbox("Select Quality:", display_formats, format_func=lambda x: x['label'])
            
            if st.button("🚀 Prepare Download"):
                safe_title = re.sub(r'[^\w\s-]', '', video_title).strip()
                filename = f"{safe_title}.{selected_option['ext']}"
                
                with st.spinner("Downloading to server and preparing file..."):
                    download_opts = {
                        'format': selected_option['id'],
                        'outtmpl': filename,
                        'quiet': True,
                    }
                    with yt_dlp.YoutubeDL(download_opts) as ydl:
                        ydl.download([url])
                    
                    with open(filename, "rb") as file:
                        st.download_button(
                            label="✅ Download to your Device",
                            data=file,
                            file_name=filename,
                            mime=f"video/{selected_option['ext']}"
                        )
                    os.remove(filename) # Clean up server space
        else:
            st.error("No direct video+audio formats found. Try another link.")

    except Exception as e:
        st.error(f"Error: {e}")

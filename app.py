import streamlit as st
from pytube import YouTube
import os

st.set_page_config(page_title="YouTube Video Downloader")

def fetch_streams(url):
    try:
        yt = YouTube(url)
        video_streams = yt.streams.filter(progressive=False, only_video=True).all()
        audio_streams = yt.streams.filter(only_audio=True).all()

        video_qualities = [f"{stream.resolution} {stream.video_codec}" for stream in video_streams]
        audio_qualities = [stream.abr for stream in audio_streams]

        return yt, video_qualities, audio_qualities
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None, None

def download_video(yt, video_quality, audio_quality, save_path):
    res, cod = video_quality.strip().split(maxsplit=1)

    stream = yt.streams.filter(res=res, video_codec=cod, progressive=False).first()
    if not stream:
        st.error("Error: Selected video quality not available")
        return None

    st.info(f"Downloading video: {stream}")
    video_file = stream.download(output_path=save_path)

    if audio_quality:
        audio_stream = yt.streams.filter(abr=audio_quality).first()
        if audio_stream:
            st.info(f"Downloading audio: {audio_stream}")
            audio_file = audio_stream.download(output_path=save_path)
            return video_file, audio_file
    
    return video_file, None

st.title("YouTube Video Downloader")

url = st.text_input("Enter YouTube URL")
if url:
    yt, video_qualities, audio_qualities = fetch_streams(url)
    if yt:
        video_quality = st.selectbox("Select video quality", video_qualities)
        download_audio = st.checkbox("Download audio")
        if download_audio:
            audio_quality = st.selectbox("Select audio quality", audio_qualities)
        else:
            audio_quality = None
        save_path = "C:\Windows\System32\cmd.exe"

        if st.button("Download"):
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            video_file, audio_file = download_video(yt, video_quality, audio_quality, save_path)
            if video_file:
                st.success("Download complete!")
                with open(video_file, "rb") as file:
                    st.download_button(label="Download Video", data=file, file_name=os.path.basename(video_file))
                if audio_file:
                    with open(audio_file, "rb") as file:
                        st.download_button(label="Download Audio", data=file, file_name=os.path.basename(audio_file))
            else:
                st.error("Error downloading the video. Please try again.")

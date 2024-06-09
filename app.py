import streamlit as st
from pytube import YouTube
import os
import moviepy.editor as mp

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
            output_file = os.path.join(save_path, f"{yt.title}.mp4")
            merge_audio_video(video_file, audio_file, output_file)
            return output_file, None
    
    return video_file, None

def merge_audio_video(video_file, audio_file, output_file):
    video_clip = mp.VideoFileClip(video_file)
    audio_clip = mp.AudioFileClip(audio_file)
    
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

st.title("YouTube Video Downloader")

url = st.text_input("Enter YouTube URL")
if url:
    yt, video_qualities, audio_qualities = fetch_streams(url)
    if yt:
        video_quality = st.selectbox("Select video quality", video_qualities)
        audio_quality = st.selectbox("Select audio quality", audio_qualities)
        save_path = "C:\Windows\System32\cmd.exe"

        if st.button("Download"):
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            video_file, _ = download_video(yt, video_quality, audio_quality, save_path)
            if video_file:
                st.success("Download complete!")
                with open(video_file, "rb") as file:
                    st.download_button(label="Download Video", data=file, file_name=os.path.basename(video_file))
            else:
                st.error("Error downloading the video. Please try again.")

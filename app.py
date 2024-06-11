import streamlit as st
from pytube import YouTube
import os
import moviepy.editor as mp

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
    try:
        res, cod = video_quality.strip().split(maxsplit=1)
        stream = yt.streams.filter(res=res, video_codec=cod, progressive=False).first()
        if not stream:
            st.error("Error: Selected video quality not available")
            return None, None

        st.info(f"Downloading video: {stream}")
        video_file = stream.download(output_path=save_path)

        audio_file = None
        if audio_quality:
            audio_stream = yt.streams.filter(abr=audio_quality).first()
            if audio_stream:
                st.info(f"Downloading audio: {audio_stream}")
                audio_file = audio_stream.download(output_path=save_path)

        return video_file, audio_file
    except Exception as e:
        st.error(f"Error during download: {str(e)}")
        return None, None

def merge_audio_video(video_file, audio_file, output_file):
    try:
        video_clip = mp.VideoFileClip(video_file)
        if audio_file:
            audio_clip = mp.AudioFileClip(audio_file)
            final_clip = video_clip.set_audio(audio_clip)
        else:
            final_clip = video_clip

        fps = video_clip.fps
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=fps, logger=None)
        return output_file
    except Exception as e:
        st.error(f"Error during merging: {str(e)}")
        return None

st.title("YouTube Video Downloader")

url = st.text_input("Enter YouTube URL")
if url:
    yt, video_qualities, audio_qualities = fetch_streams(url)
    if yt:
        video_quality = st.selectbox("Select video quality", video_qualities)
        audio_quality = st.selectbox("Select audio quality", audio_qualities)
        save_path = os.getcwd()
        download_merge = st.checkbox("Want to merge video and audio. slower!!! - only available for avc1.4d401e codec")

        if st.button("Download"):
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            video_file, audio_file = download_video(yt, video_quality, audio_quality, save_path)
            if download_merge:
                if video_file:
                    output_file = os.path.join(save_path, f"{yt.title}.mp4")
                    merged_file = merge_audio_video(video_file, audio_file, output_file)
                    if merged_file:
                        st.success("Download complete!")
                        with open(merged_file, "rb") as file:
                            st.download_button(label="Download Video", data=file, file_name=os.path.basename(merged_file))
                    else:
                        st.error("Error merging the video and audio. Please try again.")
                else:
                    st.error("Error downloading the video. Please try again.")
            else:
                with open(video_file, "rb") as file:
                    st.download_button(label="Download Video", data=file, file_name=os.path.basename(video_file))
                with open(audio_file, "rb") as file:
                    st.download_button(label="Download Audio", data=file, file_name=os.path.basename(audio_file))

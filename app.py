from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from pytube import YouTube
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def fetch_streams(url):
    try:
        yt = YouTube(url)
        video_streams = yt.streams.filter(progressive=False, only_video=True).all()
        audio_streams = yt.streams.filter(only_audio=True).all()

        video_qualities = [f"{stream.resolution} {stream.video_codec}" for stream in video_streams]
        audio_qualities = [stream.abr for stream in audio_streams]

        return yt, video_qualities, audio_qualities
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None, None

def download_video(yt, video_quality, audio_quality, save_path):
    res, cod = video_quality.strip().split(maxsplit=1)

    stream = yt.streams.filter(res=res, video_codec=cod, progressive=False).first()
    if not stream:
        print("Error: Selected video quality not available")
        return None

    print(f"Downloading video: {stream}")
    video_file = stream.download(output_path=save_path)

    if audio_quality:
        audio_stream = yt.streams.filter(abr=audio_quality).first()
        if audio_stream:
            print(f"Downloading audio: {audio_stream}")
            audio_file = audio_stream.download(output_path=save_path)
            return video_file, audio_file
    
    return video_file, None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        yt, video_qualities, audio_qualities = fetch_streams(url)

        if yt is None:
            flash('Error fetching streams. Please check the URL and try again.')
            return redirect(url_for('index'))

        return render_template('index.html', url=url, video_qualities=video_qualities, audio_qualities=audio_qualities)

    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    video_quality = request.form['video_quality']
    download_audio = 'download_audio' in request.form
    audio_quality = request.form['audio_quality'] if download_audio else None
    save_path = request.form['save_path']

    # Handle case when the save_path is from file input
    if save_path and save_path.startswith("C:\\fakepath\\"):
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(save_path))

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    yt, _, _ = fetch_streams(url)
    video_file, audio_file = download_video(yt, video_quality, audio_quality, save_path)

    if video_file:
        flash('Download complete!')
        return send_from_directory(save_path, os.path.basename(video_file), as_attachment=True)
    else:
        flash('Error downloading the video. Please try again.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

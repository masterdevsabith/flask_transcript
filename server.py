from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

@app.route('/')
def home():
    return 'Server is up'

@app.route('/transcript', methods=['POST'])
def transcript():
    data = request.json
    youtube_url = data.get('url')

    try:
        # Extract video ID from the URL
        video_id = parse_qs(urlparse(youtube_url).query).get("v", [None])[0]
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        # Fetch transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([x['text'] for x in transcript_list])

        return jsonify({'transcript': full_transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

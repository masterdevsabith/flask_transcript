import os
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Optional: Set your proxy here
PROXY = {
    'http': 'http://116.103.25.152:16000',
    'https': 'http://116.103.25.152:16000'
}

@app.route('/')
def home():
    return 'Server is up'

@app.route('/transcript', methods=['POST'])
def transcript():
    data = request.json
    youtube_url = data.get('url')
    try:
        video_id = parse_qs(urlparse(youtube_url).query).get("v", [None])[0]
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400
        
        # Now using proxies to avoid IP bans
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=PROXY)
        full_transcript = " ".join([x['text'] for x in transcript_list])
        return jsonify({'transcript': full_transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

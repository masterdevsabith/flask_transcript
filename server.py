# import os
# from flask import Flask, request, jsonify
# from youtube_transcript_api import YouTubeTranscriptApi
# from urllib.parse import urlparse, parse_qs

# app = Flask(__name__)

# # Optional: Set your proxy here
# PROXY = {
#     'http': 'http://116.103.25.152:16000',
#     'https': 'http://116.103.25.152:16000'
# }

# @app.route('/')
# def home():
#     return 'Server is up'

# @app.route('/transcript', methods=['POST'])
# def transcript():
#     data = request.json
#     youtube_url = data.get('url')
#     try:
#         video_id = parse_qs(urlparse(youtube_url).query).get("v", [None])[0]
#         if not video_id:
#             return jsonify({"error": "Invalid YouTube URL"}), 400
        
#         transcript_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=PROXY)
#         full_transcript = " ".join([x['text'] for x in transcript_list])
#         print(full_transcript)
#         return jsonify({'transcript': full_transcript})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)
import os
import requests
import traceback
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

app = Flask(__name__)

# ✅ Scrape proxies from free-proxy-list.net
def get_proxy_list():
    try:
        url = "https://free-proxy-list.net/"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        proxy_table = soup.find("table", id="proxylisttable")

        proxies = []
        for row in proxy_table.tbody.find_all("tr"):
            cols = row.find_all("td")
            ip = cols[0].text
            port = cols[1].text
            https = cols[6].text
            if https == "yes":
                proxies.append(f"http://{ip}:{port}")
        return proxies
    except Exception as e:
        print("Failed to get proxy list:", e)
        return []

# ✅ Find the first working proxy
def get_working_proxy():
    proxy_list = get_proxy_list()
    test_url = "https://www.google.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    for proxy in proxy_list[:10]:  # Limit to test top 10 for speed
        try:
            response = requests.get(
                test_url,
                proxies={"http": proxy, "https": proxy},
                timeout=3,
                headers=headers,
            )
            if response.status_code == 200:
                print(f"[+] Found working proxy: {proxy}")
                return {"http": proxy, "https": proxy}
        except Exception:
            continue
    print("[-] No working proxy found.")
    return None

@app.route('/')
def home():
    return '✅ Flask server is up and running!'

@app.route('/transcript', methods=['POST'])
def transcript():
    data = request.json
    youtube_url = data.get('url')
    if not youtube_url:
        return jsonify({'error': 'URL not provided'}), 400

    try:
        video_id = parse_qs(urlparse(youtube_url).query).get("v", [None])[0]
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        proxy = get_working_proxy()

        if proxy:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy)
        else:
            print("⚠️ Using fallback without proxy...")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        full_transcript = " ".join([x['text'] for x in transcript_list])
        return jsonify({'transcript': full_transcript})

    except Exception as e:
        print("❌ Error occurred:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

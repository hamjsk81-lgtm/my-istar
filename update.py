import requests
import re
import time

# زانیارییەکانت لێرە دابنێ
MAC = "12d7087e0000630d" # ماک ئەدێرسەکەی خۆت
SERVER_IP = "45.155.226.147" # ئایپی نوێی سێرڤەرەکە کە ئەمڕۆ گرتت

headers = {
    'User-Agent': 'iStarMedia/1.0 (Android)',
    'Cookie': f'mac={MAC}'
}

def get_new_link(channel_cmd):
    # کات زیاد دەکەین بۆ ئەوەی سێرڤەرەکە فێڵمان لێ نەکات
    url = f"http://{SERVER_IP}:8085/server/load.php?type=itv&action=create_link&cmd={channel_cmd}&_={int(time.time())}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('cmd', '')
    except Exception as e:
        print(f"Error getting link for {channel_cmd}: {e}")
    return None

# لێرەدا فایلی ئەسڵی دەخوێنینەوە
try:
    with open('channels.m3u', 'r') as f:
        content = f.read()
    
    # دۆزینەوەی هەموو لینکەکان
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    
    for old_link in links:
        # دەرهێنانی ناوی کەناڵەکە (cmd) لە لینکە کۆنەکە
        match = re.search(r'local-(.*?)/', old_link)
        if match:
            cmd = f"ffrt+http://localhost/local-{match.group(1)}/mono.m3u8"
            print(f"Updating: {match.group(1)}...")
            new_link = get_new_link(cmd)
            if new_link:
                content = content.replace(old_link, new_link)
                print(f"Successfully updated: {match.group(1)}")

    # پاشەکەوتکردنی ئەنجامەکە لە فایلی نوێدا
    with open('playlist.m3u', 'w') as f:
        f.write(content)
    print("All links updated and saved to playlist.m3u")

except Exception as e:
    print(f"Main error: {e}")

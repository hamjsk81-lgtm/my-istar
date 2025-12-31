import requests
import re
import time
import random

MAC = "12d7087e0000630d"
SERVER_IP = "45.155.226.147" # دڵنیابەرەوە ئەم ئایپییە ئیش دەکات

headers = {
    'User-Agent': 'iStarMedia/1.1 (Android; 10; Build/QP1A.190711.020)',
    'Cookie': f'mac={MAC}',
    'Accept-Encoding': 'gzip',
    'Connection': 'Keep-Alive'
}

def get_new_link(channel_cmd):
    # زیادکردنی ژمارەیەکی هەڕەمەکی بۆ ئەوەی سێرڤەرەکە وا بزانێت داواکارییەکی نوێیە
    random_str = random.randint(10000, 99999)
    url = f"http://{SERVER_IP}:8085/server/load.php?type=itv&action=create_link&cmd={channel_cmd}&_={int(time.time())}&rand={random_str}"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            link = data.get('cmd', '')
            if link and 'http' in link:
                return link
    except Exception as e:
        print(f"Error for {channel_cmd}: {e}")
    return None

try:
    # خوێندنەوەی فایلی سەرەکی
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # دۆزینەوەی هەموو ئەو شوێنانەی لینکی تێدایە
    old_links = re.findall(r'http://[0-9.]+:8085/.*?info=' + MAC, content)
    
    updated_count = 0
    for old_link in set(old_links): # بەکارهێنانی set بۆ ئەوەی لینکە دووبارەکان لادەین
        match = re.search(r'local-(.*?)/', old_link)
        if match:
            channel_id = match.group(1)
            cmd = f"ffrt+http://localhost/local-{channel_id}/mono.m3u8"
            print(f"Requesting new link for: {channel_id}")
            
            new_link = get_new_link(cmd)
            if new_link and new_link != old_link:
                content = content.replace(old_link, new_link)
                updated_count += 1
                print(f"Done: {channel_id}")
            else:
                print(f"No new link for: {channel_id} (Server returned same link)")

    # پاشەکەوتکردن
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Total updated links: {updated_count}")
    print("Finished. Saved to playlist.m3u")

except Exception as e:
    print(f"Main Error: {e}")

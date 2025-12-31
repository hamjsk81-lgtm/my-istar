import requests
import re
import time
import random

# زانیارییەکان
MAC = "12d7087e0000630d"
SERVER_IP = "45.155.226.147"

headers = {
    'User-Agent': 'iStarMedia/1.1 (Android; 10)',
    'Cookie': f'mac={MAC}',
    'Connection': 'Keep-Alive'
}

def get_new_link(channel_cmd):
    # زیادکردنی کات و ژمارەی هەڕەمەکی بۆ ڕێگری لە کاش (Cache)
    timestamp = int(time.time())
    random_str = random.randint(1000, 9999)
    url = f"http://{SERVER_IP}:8085/server/load.php?type=itv&action=create_link&cmd={channel_cmd}&_={timestamp}&r={random_str}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            link = data.get('cmd', '')
            if link and 'http' in link:
                return link
    except Exception as e:
        print(f"Error fetching {channel_cmd}: {e}")
    return None

try:
    # ١. خوێندنەوەی فایلی سەرەکی کە لینکە کۆنەکانی تێدایە
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ٢. دۆزینەوەی هەموو ئەو لینکە ئایستارانەی کە ماک ئەدێرسەکەی تۆیان پێوەیە
    # ئەم شێوازە هەموو جۆرە ئایپی و لینکێکی ئایستار دەدۆزێتەوە
    old_links = re.findall(r'http://[0-9.]+:8085/.*?info=' + MAC, content)
    
    updated_count = 0
    # لابردنی لینکە دووبارەکان بۆ ئەوەی خێرا بێت
    unique_links = list(set(old_links))
    
    print(f"Found {len(unique_links)} unique channels to update.")

    for old_link in unique_links:
        # دەرهێنانی ناسنامەی کەناڵەکە (local-xxxx)
        match = re.search(r'local-(.*?)/', old_link)
        if match:
            channel_id = match.group(1)
            cmd = f"ffrt+http://localhost/local-{channel_id}/mono.m3u8"
            
            new_link = get_new_link(cmd)
            if new_link:
                content = content.replace(old_link, new_link)
                updated_count += 1
                print(f"Updated: {channel_id}")

    # ٣. پاشەکەوتکردنی ئەنجامەکە لە فایلی playlist.m3u
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(content)
        # ٤. دێڕێکی کاتی زیادە بۆ ئەوەی گیتھەب هەمیشە گۆڕانکارییەکە ببینێت
        f.write(f"\n\n# Last Sync: {time.strftime('%Y-%m-%d %H:%M:%S')} (Baghdad Time)\n")
    
    print(f"--- SUCCESS: {updated_count} links processed ---")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")

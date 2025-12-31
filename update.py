import requests
import re
import time
import random

MAC = "12d7087e0000630d"

headers = {
    'User-Agent': 'iStarMedia/1.1 (Android; 10)',
    'Cookie': f'mac={MAC}',
    'Connection': 'Keep-Alive'
}

def get_new_link(server_ip, channel_id):
    timestamp = int(time.time())
    random_str = random.randint(1000, 9999)
    cmd = f"ffrt+http://localhost/local-{channel_id}/mono.m3u8"
    url = f"http://{server_ip}:8085/server/load.php?type=itv&action=create_link&cmd={cmd}&_={timestamp}&r={random_str}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            link = data.get('cmd', '')
            if link and 'http' in link:
                return link
    except:
        pass
    return None

try:
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_content = ""
    updated_count = 0

    print("Starting update process...")

    for line in lines:
        # ئەگەر دێڕەکە لینکی ئایستار بوو
        if "local-" in line and "info=" + MAC in line:
            # دەرهێنانی ئایپی و ناسنامەی کەناڵ
            match = re.search(r'http://([0-9.]+):8085/.*?local-(.*?)/', line)
            if match:
                ip = match.group(1)
                channel_id = match.group(2)
                
                print(f"Fetching: {channel_id} ({ip})")
                new_link = get_new_link(ip, channel_id)
                
                if new_link:
                    new_content += new_link + "\n"
                    updated_count += 1
                else:
                    # ئەگەر لینکە نوێیەکە وەرنەگیرا، هەمان کۆنەکە دابنێوە بۆ ئەوەی کەناڵەکە نەفەوتێت
                    new_content += line
            else:
                new_content += line
        else:
            # ئەگەر دێڕی ئاسایی بوو (وەک ناوی کەناڵ #EXTINF)
            new_content += line

    # نووسینەوەی هەموو ناوەڕۆکەکە لە فایلێکی نوێدا
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(new_content)
        f.write(f"\n# Last Update: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"--- Processed {updated_count} links ---")

except Exception as e:
    print(f"Error: {e}")

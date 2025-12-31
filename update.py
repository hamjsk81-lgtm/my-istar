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
    """داواکردنی لینکی نوێ لەو سێرڤەرەی کە کەناڵەکەی لەسەرە"""
    timestamp = int(time.time())
    random_str = random.randint(1000, 9999)
    cmd = f"ffrt+http://localhost/local-{channel_id}/mono.m3u8"
    
    # بەکارهێنانی ئەو ئایپییەی کە لە لینکە ئەسڵییەکەدا دۆزراوەتەوە
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
    # ١. خوێندنەوەی فایلی سەرەکی
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ٢. دۆزینەوەی هەموو ئەو لینکە ئایستارانەی کە ماک ئەدێرسەکەی تۆیان پێوەیە
    # ئەم نەخشەیە ئایپی و ناوی کەناڵەکە پێکەوە دەردەهێنێت
    # وەک: http://103.163.132.12:8085/.../local-Rasan-H265/...
    pattern = r'(http://([0-9.]+):8085/.*?local-(.*?)/mono\.m3u8\?md5=.*?info=' + MAC + r')'
    all_matches = re.findall(pattern, content)
    
    print(f"Found {len(all_matches)} links in total.")

    updated_count = 0
    # لابردنی لینکە دووبارەکان بۆ ئەوەی سێرڤەرەکە لێمان تووڕە نەبێت
    processed_links = {}

    for full_link, ip, channel_id in all_matches:
        if full_link not in processed_links:
            print(f"Updating: {channel_id} on Server: {ip}")
            new_link = get_new_link(ip, channel_id)
            
            if new_link:
                # گۆڕینی هەموو نموونەکانی ئەم لینکە لەناو دەقەکەدا
                content = content.replace(full_link, new_link)
                processed_links[full_link] = new_link
                updated_count += 1

    # ٣. پاشەکەوتکردنی ئەنجامەکە لە فایلی نوێدا
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(content)
        # زیادکردنی دێڕی کات بۆ ئەوەی گیتھەب هەموو جارێک پاشەکەوتی بکات
        f.write(f"\n\n# Auto Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"--- SUCCESS: {updated_count} unique links updated ---")

except Exception as e:
    print(f"Error: {e}")

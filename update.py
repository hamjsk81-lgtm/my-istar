import requests
import re
import time
import random

MAC = "12d7087e0000630d"

def get_new_link(server_ip, channel_id):
    # تاقی کردنەوەی پۆرتی جیاواز ئەگەر 8085 کاری نەکرد
    url = f"http://{server_ip}:8085/server/load.php?type=itv&action=create_link&cmd=ffrt+http://localhost/local-{channel_id}/mono.m3u8&_={int(time.time())}"
    
    headers = {
        'User-Agent': 'iStarMedia/1.1 (Android; 10; Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36',
        'Cookie': f'mac={MAC}',
        'X-Requested-With': 'com.istar.istarmedia',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': f'http://{server_ip}:8085/system/index.html',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    try:
        # بەکارھێنانی ڕێگای ئاسایی بەبێ پۆرت ئەگەر یەکەمیان سەرکەوتوو نەبوو
        response = requests.get(url, headers=headers, timeout=15)
        
        # ئەگەر پۆرتی 8085 کاری نەکرد (404)، پۆرتی 80 تاقی دەکەینەوە
        if response.status_code != 200:
            url_alt = url.replace(":8085", "")
            response = requests.get(url_alt, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data.get('cmd', '')
    except:
        pass
    return None

try:
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'(http://[0-9.]+(:8085)?/.*?local-(.*?)/mono\.m3u8\?.*?info=' + MAC + r')'
    matches = re.findall(pattern, content)
    
    print(f"Found {len(matches)} channels. Attempting to bypass block...")
    
    update_count = 0
    for full_link, port_part, channel_id in matches:
        server_ip = re.search(r'http://([0-9.]+)', full_link).group(1)
        
        new_link = get_new_link(server_ip, channel_id)
        
        if new_link and 'http' in new_link and new_link != full_link:
            content = content.replace(full_link, new_link)
            update_count += 1
            print(f"Update Success: {channel_id}")

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(content)
        f.write(f"\n# Sync: {time.ctime()} | Success: {update_count}")
    
    print(f"Done! Total: {update_count} links updated.")

except Exception as e:
    print(f"Error: {e}")

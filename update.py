import requests
import re
import time
import json

MAC = "12d7087e0000630d"

def get_new_link(server_ip, channel_id):
    # بەکارهێنانی ناونیشانی load.php بەڵام بەبێ پۆرتی 8085 وەک مۆبایل
    url = f"http://{server_ip}/server/load.php?type=itv&action=create_link&cmd=ffrt+http://localhost/local-{channel_id}/mono.m3u8"
    
    headers = {
        'User-Agent': 'iStarMedia/1.1 (Android; 10)',
        'Cookie': f'mac={MAC}',
        'X-Requested-With': 'com.istar.istarmedia',
        'Accept': 'application/json'
    }
    
    try:
        # زیادکردنی پشکنینی وەڵامی سێرڤەر
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            res_text = response.text
            # ئەگەر سێرڤەر وەڵامی JSON دایەوە
            if '"cmd":' in res_text:
                data = response.json()
                return data.get('cmd', '')
    except:
        pass
    return None

try:
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # دۆزینەوەی هەموو لینکەکان بە شێوەی ورد
    pattern = r'(http://[0-9.]+(:8085)?/.*?local-(.*?)/mono\.m3u8\?.*?info=' + MAC + r')'
    matches = re.findall(pattern, content)
    
    print(f"Found {len(matches)} channels. Updating...")
    
    update_count = 0
    for full_link, port_part, channel_id in matches:
        server_ip = re.search(r'http://([0-9.]+)', full_link).group(1)
        
        new_link = get_new_link(server_ip, channel_id)
        
        # تەنها ئەگەر لینکەکە نوێ بوو و بەتاڵ نەبوو، بیگۆڕە
        if new_link and 'http' in new_link:
            content = content.replace(full_link, new_link)
            update_count += 1
            if "Rasan" in channel_id:
                print(f"Successfully updated Rasan!")

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(content)
        f.write(f"\n# Updated: {time.ctime()} | Links Updated: {update_count}")
    
    print(f"Done! Updated {update_count} links.")

except Exception as e:
    print(f"Error: {e}")

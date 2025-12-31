import requests
import re
import time

MAC = "12d7087e0000630d"

def get_new_link(server_ip, channel_id):
    # ئەمە ئەو ناونیشانە نوێیەیە کە ئایستار ئێستا بەکاری دێنێت (بەبێ پۆرتی 8085)
    url = f"http://{server_ip}/portal.php?type=itv&action=create_link&cmd=ffrt+http://localhost/local-{channel_id}/mono.m3u8"
    
    headers = {
        'User-Agent': 'iStarMedia/1.1 (Android; 10)',
        'Cookie': f'mac={MAC}',
        'X-Requested-With': 'com.istar.istarmedia'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('cmd', '')
    except:
        pass
    return None

try:
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # دۆزینەوەی هەموو لینکەکان
    pattern = r'(http://[0-9.]+(:8085)?/.*?local-(.*?)/mono\.m3u8\?.*?info=' + MAC + r')'
    matches = re.findall(pattern, content)
    
    print(f"Found {len(matches)} channels. Updating...")

    for full_link, port_part, channel_id in matches:
        # درێژەی ئایپیەکە لێرە دەردەهێنین
        server_ip = re.search(r'http://([0-9.]+)', full_link).group(1)
        
        new_link = get_new_link(server_ip, channel_id)
        if new_link:
            content = content.replace(full_link, new_link)

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(content)
        f.write(f"\n# Updated: {time.ctime()}")
    
    print("Done! Check your playlist.m3u")

except Exception as e:
    print(f"Error: {e}")

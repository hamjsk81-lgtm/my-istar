import requests
import re
import time
import random

MAC = "12d7087e0000630d"

def get_new_link(server_ip, channel_id):
    timestamp = int(time.time())
    # دروستکردنی Token ی هەڕەمەکی بۆ ئەوەی وەک مۆبایل دەرکەوێت
    random_str = random.randint(100, 999)
    cmd = f"ffrt+http://localhost/local-{channel_id}/mono.m3u8"
    url = f"http://{server_ip}:8085/server/load.php?type=itv&action=create_link&cmd={cmd}&_={timestamp}&r={random_str}"
    
    # ئەم بەشە زۆر گرنگە بۆ تێپەڕاندنی بلۆک
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36',
        'Cookie': f'mac={MAC}',
        'X-Requested-With': 'com.istar.istarmedia',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    
    try:
        # بەکارهێنانی timeout ی کەمێک درێژتر
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # چاپکردنی ئەنجامەکە بۆ ئەوەی بزانین بۆچی 0 دەدات
            print(f"Server response for {channel_id}: {data}") 
            link = data.get('cmd', '')
            if link and 'http' in link:
                return link
        else:
            print(f"Failed {channel_id}: Status {response.status_code}")
    except Exception as e:
        print(f"Error {channel_id}: {str(e)}")
    return None

try:
    with open('channels.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_content = ""
    updated_count = 0

    print("Starting update process with Advanced Headers...")

    for line in lines:
        if "local-" in line and "info=" + MAC in line:
            match = re.search(r'http://([0-9.]+):8085/.*?local-(.*?)/', line)
            if match:
                ip = match.group(1)
                channel_id = match.group(2)
                
                new_link = get_new_link(ip, channel_id)
                
                if new_link:
                    new_content += new_link + "\n"
                    updated_count += 1
                else:
                    new_content += line # ئەگەر نەگیرا، کۆنەکە بپارێزە
            else:
                new_content += line
        else:
            new_content += line

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(new_content)
        f.write(f"\n# Last Update: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"--- SUCCESS: {updated_count} links updated ---")

except Exception as e:
    print(f"Main Error: {e}")

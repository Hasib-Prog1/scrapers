from parsel import Selector
import requests
import json
import time
import re
import datetime
def get_data(urls):
    if isinstance(urls, str):
        urls = [urls] 
        print(urls)
        
    all_data = []
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="141.0.7390.108", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"10.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    }

    all_data = []
    for url in urls:
        max_try = 3
        err_list = None
        response = None

        print(f"Processing URL: {url}")


        for i in range(max_try):
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    response = resp
                    break
                else:
                    err_list = Exception(f"Non-200 status code: {resp.status_code}")
            except Exception as e:
                err_list = e
                time.sleep(1)

        if response is None:
            print(f"⚠️ Failed to fetch {url}: {err_list if err_list else 'Request failed'}")
            continue

        selector = Selector(text=response.text)

        scripts = selector.css('script[type="application/json"][data-content-len][data-sjs]::text').getall()
        all_data.extend(scripts)


    return all_data




urls = ["https://www.facebook.com/reel/2051489205656843", 
        "https://www.facebook.com/reel/1875178263081112",
        "https://www.facebook.com/reel/2051489205656843",
        "https://www.facebook.com/reel/1372521511118228",
       ]




# for url in urls:
#     data = get_data(url)   

# Get data from all URLs

def contains_best_description(obj):
    """Recursively check if 'best_description' exists anywhere inside a JSON object"""
    if isinstance(obj, dict):
        if "associated_group" in obj:
            return True
        return any(contains_best_description(v) for v in obj.values())
    elif isinstance(obj, list):
        return any(contains_best_description(i) for i in obj)
    return False

final_list = []

for url in urls:

    all_scripts = get_data(url)

    parsed_data = []
    for item in all_scripts:  
        if isinstance(item, str):
            try:
                parsed_data.append(json.loads(item))
            except json.JSONDecodeError:
                continue
        elif isinstance(item, dict):
            parsed_data.append(item)

    filtered = [item for item in parsed_data if contains_best_description(item)]

    filtered = [item for item in parsed_data if contains_best_description(item)]

    # Remove saving & reading
    data = filtered

    print(f"✅ Done! Found {len(filtered)} JSON objects containing 'best_description'.")

    def find_value(obj, target_path):
        if not target_path:
            return None

        key = target_path[0]

        if isinstance(obj, dict):
            if key in obj:
                if len(target_path) == 1:
                    return obj[key]
                else:
                    return find_value(obj[key], target_path[1:])
            
            for v in obj.values():
                result = find_value(v, target_path)
                if result is not None:
                    return result

        elif isinstance(obj, list):
            for item in obj:
                result = find_value(item, target_path)
                if result is not None:
                    return result

        return None


    caption_path = ["result", "data", "video", "creation_story", "message", "text"]
    thumbnail_path = [
        "result", "data", "video", "creation_story",
        "short_form_video_context", "playback_video",
        "thumbnailImage", "uri"
    ]
    video_id_path = [
        "result", "data", "video", "creation_story",
        "short_form_video_context", "playback_video", "id"
    ]

    caption = find_value(data, caption_path)
    thumbnail = find_value(data, thumbnail_path)
    video_id = find_value(data, video_id_path)

    if caption:
        print(" Caption found:", caption)
    else:
        print(" Caption not found.")
    if thumbnail:
        print(" Thumbnail found:", thumbnail)
    else:
        print(" Thumbnail not found.")

    if video_id:
        print(" Video ID found:", video_id)
    else:
        print(" Video ID not found.")

    comment_count_path = ["result", "data", "feedback", "total_comment_count"]


    comment_count = find_value(data, comment_count_path)

    if comment_count is not None:
        print("✅ Total Comment Count Found:", comment_count)
    else:
        print("⚠️ Total Comment Count not found in JSON.")

    likers_path = ["result", "data", "fb_reel_react_button", "story", "feedback", "likers"]

    likers = find_value(data, likers_path)

    if likers:
        print(" Likers data found:")
        print(json.dumps(likers, indent=4, ensure_ascii=False))
    else:
        print(" Likers data not found in JSON.")    


    share_count_path = ["result", "data", "feedback", "share_count_reduced"]
    share_count = find_value(data, share_count_path)

    if share_count is not None:
        print(" Share Count Found:", share_count)
    else:
        print("⚠️ Share Count not found in JSON.")


    owner_name_path = ["result", "data", "video", "creation_story", "short_form_video_context", "video_owner", "name"]

    # Add this with your other variables
    owner_name = find_value(data, owner_name_path)

    # And finally, print it
    if owner_name:
        print(" Video Owner Name found:", owner_name)
    else:
        print(" Video Owner Name not found in JSON.")   



    if caption:
        
        hashtags = re.findall(r"#\w+", caption)

        if hashtags:
            print(" Extracted Hashtags:")
            for tag in hashtags:
                print(tag)
        else:
            print(" No hashtags found in caption.")
    else:
        print(" No caption found to extract hashtags from.")

    shareable_url_path = [
        "result", "data", "video", "creation_story",
        "short_form_video_context", "shareable_url"
    ]

    shareable_url = find_value(data, shareable_url_path)


    if shareable_url:
        print(" Shareable URL found:", shareable_url)
    else:
        print(" Shareable URL not found in JSON.")    

    def find_value_by_key(obj, key):
        """Recursively search any key inside nested JSON"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    return v
                result = find_value_by_key(v, key)
                if result is not None:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = find_value_by_key(item, key)
                if result is not None:
                    return result
        return None



    timestamp = find_value_by_key(data, "creation_time") or find_value_by_key(data, "creation_date")

    if timestamp:
        if isinstance(timestamp, int) or str(timestamp).isdigit():
            date_time = datetime.datetime.fromtimestamp(int(timestamp))
            reelDateTime = date_time.strftime("%Y-%m-%d %H:%M:%S")
            reelDate = date_time.strftime("%Y-%m-%d")
            print(" Reel DateTime:", reelDateTime)
            print(" Reel Date:", reelDate)
        else:
            print(" Reel Creation:", timestamp)
    else:
        print(" কোনো creation_time বা creation_date পাওয়া যায়নি।")

    reelDuration = (
        find_value_by_key(data, "video_duration")
        or find_value_by_key(data, "play_duration")
        or find_value_by_key(data, "length")
        or find_value_by_key(data, "duration")
    )

    if reelDuration:
        print(f" Reel Duration: {reelDuration} seconds")
    else:
        print(" no duration found.")





    final_output = {
        "caption": caption,
        "thumbnail": thumbnail,
        "video_id": video_id,
        "comment_count": comment_count,
        "like_count": likers,
        "share_count": share_count,
        "owner_name": owner_name,
        "hashtags": hashtags ,
        "shareable_url": shareable_url,
        "reelDateTime": reelDateTime ,
        "reelDate": reelDate,
        "reelDuration": reelDuration
    }
    final_list.append(final_output)

    print(final_output)

    print("----" * 50)

# Save to output.json
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f, indent=4, ensure_ascii=False)

print("\n data saved successfully to output.json")
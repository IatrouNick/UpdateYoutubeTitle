import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def load_config(config_file='config.json'):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def get_uploads_playlist_id(api_key, channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            return uploads_playlist_id
        else:
            print("No channel found with the specified ID.")
            return None
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None

def get_all_videos(api_key, playlist_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        videos = []
        next_page_token = None
        
        while True:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            videos.extend(response['items'])
            next_page_token = response.get('nextPageToken')
            
            if next_page_token is None:
                break
        
        return videos
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []

def get_video_details(api_key, video_ids):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        video_details = []
        for i in range(0, len(video_ids), 50):  # API allows up to 50 ids at a time
            request = youtube.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids[i:i+50])
            )
            response = request.execute()
            video_details.extend(response['items'])
        
        return video_details
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []

def main():
    config = load_config()
    api_key = config['api_key']
    channel_id = config['channel_id']
    
    uploads_playlist_id = get_uploads_playlist_id(api_key, channel_id)
    if uploads_playlist_id is None:
        return
    
    videos = get_all_videos(api_key, uploads_playlist_id)
    video_ids = [video['contentDetails']['videoId'] for video in videos]
    
    video_details = get_video_details(api_key, video_ids)
    
    video_details.sort(key=lambda x: int(x['statistics']['viewCount']), reverse=True)
    
    # Print the results to the console
    print(f"Total number of videos: {len(video_ids)}\n")
    for video in video_details:
        title = video['snippet']['title']
        views = video['statistics']['viewCount']
        print(f"Title: {title}, Views: {views}")
    
    # Write the results to a text file with UTF-8 encoding
    with open('video_details.txt', 'w', encoding='utf-8') as file:
        file.write(f"Total number of videos: {len(video_ids)}\n\n")
        for video in video_details:
            title = video['snippet']['title']
            views = video['statistics']['viewCount']
            file.write(f"Title: {title}, Views: {views}\n")

if __name__ == '__main__':
    main()

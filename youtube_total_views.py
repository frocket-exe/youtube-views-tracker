from googleapiclient.discovery import build
import json
import os

API_KEY = os.getenv("API_KEY")
PLAYLIST_ID = "PLji0kmxsfSDxyn9ctLCg4wFPMypje5GjC"

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_ids(playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        pl_request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()

        for item in pl_response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = pl_response.get("nextPageToken")

        if not next_page_token:
            break

    return video_ids


def get_total_views(video_ids):
    total_views = 0
    unique_videos = 0

    for i in range(0, len(video_ids), 50):  # API limit: 50 IDs per request
        request = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids[i:i+50])
        )
        response = request.execute()

        for video in response["items"]:
            total_views += int(video["statistics"]["viewCount"])
            unique_videos += 1

    return total_views, unique_videos


if __name__ == "__main__":
    ids = get_video_ids(PLAYLIST_ID)
    total, noOfVids = get_total_views(ids)
    print(f"Total Views: {total:,}")
    print(f"across {noOfVids} different videos")

with open("views.json", "w") as f:
    json.dump({
        "total_views": total,
        "video_count": noOfVids
    }, f, indent=2)
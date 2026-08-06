from googleapiclient.discovery import build
import os

API_KEY = os.getenv("API_KEY")
LONG_PLAYLIST_ID = "PLji0kmxsfSDxyn9ctLCg4wFPMypje5GjC"
SHORT_PLAYLIST_ID = "PLYQy0DHmqKec"

youtube = build('youtube', 'v3', developerKey=API_KEY)

def getVideoIDs(playlistID):
    video_ids = []
    next_page_token = None

    while True:
        pl_request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlistID,
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


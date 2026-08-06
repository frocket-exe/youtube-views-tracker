from googleapiclient.discovery import build
import os
from datetime import datetime
import json

API_KEY = os.getenv("API_KEY")
LONG_PLAYLIST_ID = "PLji0kmxsfSDxyn9ctLCg4wFPMypje5GjC"
SHORT_PLAYLIST_ID = "PLYQy0DHmqKec"
LONG_JSON_PATH = "views/yt_views.json"
SHORT_JSON_PATH = "views/yt-short_views.json"
SESSION_QUOTA_USED = 0

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
        global SESSION_QUOTA_USED
        SESSION_QUOTA_USED += 1

        for item in pl_response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = pl_response.get("nextPageToken")

        if not next_page_token:
            break

    return video_ids


def getVideoData(videoIDs):
    videos = []
    for i in range(0, len(videoIDs), 50):
        request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(videoIDs[i:i+50])
        )
        response = request.execute()
        global SESSION_QUOTA_USED
        SESSION_QUOTA_USED += 1

        for video in response["items"]:
            videoObj = {"url": video["id"], "creator": video["snippet"]["channelTitle"], "channelID": video["snippet"]["channelId"], "views": video["statistics"]["viewCount"]}
            videos.append(videoObj)
    return videos


def getVPS(filePath):
    with open(filePath) as f:
        json_data = json.load(f)
        prevViews = json_data["totalViews"]
        lastUpdate = json_data["timestamp"]
        vpsHistory = json_data["vpsHistory"]
    return {"prevViews": prevViews, "lastUpdate": lastUpdate, "vpsHistory": vpsHistory}

def getTotals(videoList, prevData):
    totalViews = 0
    videoCount = 0
    timestamp = int(datetime.now().timestamp())
    for video in videoList:
        totalViews += int(video["views"])
        videoCount += 1
    viewChange = totalViews - prevData["prevViews"]
    vpsHistory = prevData["vpsHistory"]
    if viewChange > 0:
        timeChange = timestamp - prevData["lastUpdate"]
        vps = round(viewChange/timeChange, 4)
        vpsHistory.pop(0)
        vpsHistory.append(vps)
    calcVps = sorted(vpsHistory)[1]

    return {"totalViews": totalViews, "videoCount": videoCount, "timestamp": timestamp, "calcVPS": calcVps, "vpsHistory": vpsHistory, "videos": videoList}


def yt_update():
    global LONG_PLAYLIST_ID
    global SHORT_PLAYLIST_ID
    global LONG_JSON_PATH
    global SHORT_JSON_PATH

    LONG_VIDEO_IDs = (getVideoIDs(LONG_PLAYLIST_ID))
    longVideoData = getVideoData(LONG_VIDEO_IDs)
    longPrevData = getVPS(LONG_JSON_PATH)
    longJson = getTotals(longVideoData, longPrevData)
    with open(LONG_JSON_PATH, "w") as f:
        json.dump(longJson, f, indent=4)

    SHORT_VIDEO_IDs = (getVideoIDs(SHORT_PLAYLIST_ID))
    shortVideoData = getVideoData(SHORT_VIDEO_IDs)
    shortPrevData = getVPS(SHORT_JSON_PATH)
    shortJson = getTotals(shortVideoData, shortPrevData)
    with open(SHORT_JSON_PATH, "w") as f:
        json.dump(shortJson, f, indent=4)

    print(f"Session tokens used: {SESSION_QUOTA_USED}")

yt_update()
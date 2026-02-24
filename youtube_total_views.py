from googleapiclient.discovery import build
import json
import os
from datetime import datetime, timedelta
from math import floor

API_KEY = os.getenv("API_KEY")
PLAYLIST_ID = "PLji0kmxsfSDxyn9ctLCg4wFPMypje5GjC"

with open("views.json") as f:
    json_data = json.load(f)
    prevViews = json_data["main"]["total_views"]
    prevTime = json_data["estimation"]["timestamp"]
    prevVPS = json_data["estimation"]["calc_vps"]
    prevOverest = json_data["estimation"]["overestimate"]
    vpsList = json_data["estimation"]["vps_history"]
    print(len(vpsList))

prevTime = datetime.strptime(prevTime, "%d/%m/%Y, %H:%M:%S")

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

def secondsBetween(t1, t2):
    timeDiff = t2 - t1
    seconds = timedelta.total_seconds(timeDiff)
    roundSeconds = floor(seconds)
    return roundSeconds

if __name__ == "__main__":
    ids = get_video_ids(PLAYLIST_ID)
    total, noOfVids = get_total_views(ids)
    viewChange = total-prevViews
    current_time = datetime.now()
    timeString = current_time.strftime("%d/%m/%Y, %H:%M:%S")
    updateInterval = secondsBetween(prevTime, current_time)
    viewsPerSecond = round((viewChange/updateInterval), 4)
    vpsList.pop(0)
    vpsList.append(viewsPerSecond)
    sorted_vpsList = sorted(vpsList)
    calcVps = sorted_vpsList[1]
    overestimation = round(prevViews + (prevVPS*updateInterval))
    if overestimation <= prevOverest:
        overestimation = prevOverest+1
    print(f"Total Views: {total:,}")
    print(f"across {noOfVids:,} different videos")
    print(f"\n{viewChange:,} new views since last update")
    print(f"as of {timeString}")
    print(f"{updateInterval:,} seconds since last update", end=" ")
    if updateInterval > 60:
        hoursInt = floor(updateInterval/(60*60))
        minutesInt = floor(updateInterval/60)-60*hoursInt
        secondsInt = floor(updateInterval%60)
        print("(", end="")
        if hoursInt > 0:
            print(f"{hoursInt}h, ", end="")
        print(f"{minutesInt}m and {secondsInt}s)")
    print(f"averaged {viewsPerSecond:,} views per second")
    print(f"Last 8 VPSs: {vpsList}")
    print(f"Sorted list of VPSs: {sorted_vpsList}")
    print(f"Calculated VPS is {calcVps}")
    print(f"\nHighest estimated views is {overestimation:,}")
    print(f"overestimated by {overestimation-total:,}")
    print(f"Corrective scale: {round(viewChange/(overestimation-prevViews), 3)}")

json_main = {
    "total_views": total,
    "video_count": noOfVids
}

json_est = {
    "calc_vps":calcVps,
    "view_change": viewChange,
    "timestamp": timeString,
    "overestimate": overestimation,
    "vps_history":vpsList
}

with open("views.json", "w") as f:
    json.dump({
        "main":json_main,
        "estimation":json_est
    }, f, indent=2)

from googleapiclient.discovery import build
import json
import os
from datetime import datetime, timedelta
from math import floor
from milestone_email import email
from pytz import timezone

API_KEY = os.getenv("API_KEY")
PLAYLIST_ID = "PLji0kmxsfSDxyn9ctLCg4wFPMypje5GjC"

with open("views.json") as f:
    json_data = json.load(f)
    prevViews = json_data["main"]["total_views"]
    prevTime = json_data["main"]["timestamp"]
    vpsList = json_data["estimation"]["vps_history"]

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

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids[i:i+50])
        )
        response = request.execute()

        for video in response["items"]:
            total_views += int(video["statistics"]["viewCount"])
            unique_videos += 1

    return total_views, unique_videos

ids = get_video_ids(PLAYLIST_ID)
total, noOfVids = get_total_views(ids)

viewChange = total-prevViews
tz = timezone('Europe/London')
current_time = int(datetime.now().timestamp())
local_time = datetime.now(tz)
localTimeString = local_time.strftime("%d/%m/%Y, %H:%M:%S")
updateInterval = (current_time-prevTime)
viewsPerSecond = round((viewChange/updateInterval), 4)

if viewsPerSecond > 0:
    vpsList.pop(0)
    vpsList.append(viewsPerSecond)
sorted_vpsList = sorted(vpsList)
calcVps = sorted_vpsList[1] 


json_main = {
    "total_views": total,
    "video_count": noOfVids,
    "timestamp": current_time
}

json_est = {
    "calc_vps":calcVps,
    "vps_history":vpsList
}

with open("views.json", "w") as f:
    json.dump({
        "main":json_main,
        "estimation":json_est
    }, f, indent=2)


print(f"\nTotal Views: {total:,}")
print(f"across {noOfVids:,} different videos")
print(f"as of {localTimeString}")

print(f"\n{viewChange:,} new views since last update")
print(f"{updateInterval:,} seconds since last update", end=" ")
if updateInterval > 60:
    hoursInt = floor(updateInterval/(60*60))
    minutesInt = floor(updateInterval/60)-60*hoursInt
    secondsInt = floor(updateInterval%60)
    print("(", end="")
    if hoursInt > 0:
        print(f"{hoursInt}h, ", end="")
        emailSubject = (f"WARNING: SERVER DOWN")
        emailBody = (f"\nThe server has been down for {hoursInt}h, {minutesInt}mi and {secondsInt}s\n")
        email(emailSubject, emailBody)
    print(f"{minutesInt}m and {secondsInt}s)")
else:
    print()
print(f"averaged {viewsPerSecond:,} views per second")

print(f"\nLast 8 VPSs: {vpsList}")
print(f"Sorted VPSs: {sorted_vpsList}")
print(f"Calculation VPS is {calcVps}")

currentYear = int((datetime.now()).strftime("%Y"))
jan1 = int(datetime(currentYear, 1, 1).timestamp())
secsThisYear = current_time-jan1

def calcJan1Views(year):
    jan1Views = floor(total - (calcVps*secsThisYear))
    return jan1Views

with open("yearStartViews.json") as f:
    json_data = json.load(f)
    try:
        prevYearViews = json_data[str(currentYear)]
    except:
        jan1Views = calcJan1Views(currentYear)
        json_data.update({str(currentYear): jan1Views})
        with open("yearStartViews.json", "w") as f:
            json.dump(json_data, f, indent=2)
            prevYearViews = jan1Views
f.close()

dec31 = int(datetime(currentYear, 12, 31, 23, 59, 59).timestamp())
meanVPS = (total-prevYearViews)/secsThisYear
viewsPerDay = floor(meanVPS*60*60*24)
meanVPS = round(meanVPS, 4)
print(f"\n{meanVPS:,} views per second mean")
print(f"{viewsPerDay:,} views per day mean")
estEnd = floor((dec31-current_time)*meanVPS+total)
print(f"{estEnd:,} views by the end of the year\n")

with open("milestones.json") as f:
    json_data = json.load(f)
    past = json_data["past"]
    future = json_data["future"]

def milestoneDate(milestone):
    viewsToGet = milestone-total
    secsLeft = viewsToGet/meanVPS
    minsLeft = round(secsLeft/60)
    maxEmailTime = 120
    if secsLeft <= 60*maxEmailTime:
        emailSubject = (f"Upcoming milestone - {milestone:,}")
        emailBody = (f"\nYou will achieve {milestone:,} views in {minsLeft} minutes\n")
        email(emailSubject, emailBody)
        print("Email sent - upcoming\n")
    milestoneDay = local_time + timedelta(minutes = minsLeft)
    milestoneDay = milestoneDay.strftime("%d/%m/%Y   %H:%M")
    print(f"{milestone:,} views  -  {milestoneDay}")

def pastMilestoneDate(milestone):
    overBy = total-milestone
    secondsSince = floor(overBy/viewsPerSecond)
    milestoneTimestamp = local_time - timedelta(seconds=secondsSince)
    milestoneTimestamp = milestoneTimestamp.strftime("%d/%m/%Y, %H:%M")
    print(f"Achieved {milestone:,} at {milestoneTimestamp}\n")
    emailSubject = (f"Achieved milestone - {milestone:,}")
    emailBody = (f"\nYou achieved {milestone:,} views on {milestoneTimestamp}\n")
    email(emailSubject, emailBody)
    print("Email sent - achieved\n")
    return milestoneTimestamp

print("Upcoming Milestones:")
for milestoneViews in [i for i in future]:
    if total >= milestoneViews:
        past.update({str(f"{milestoneViews:,}") : pastMilestoneDate(milestoneViews)})
        future.remove(milestoneViews)
    else:
        milestoneDate(milestoneViews)

print()

with open("milestones.json", "w") as f:
    json.dump({
    "past":past,
    "future":future
}, f, indent=2)

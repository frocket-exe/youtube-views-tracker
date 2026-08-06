# https://github.com/davidteather/TikTok-Api
import json

def getTotals(videos):
    totalViews = 0
    videoCount = 0
    uniqueVideoCount = 0
    for video in videos:
        totalViews += int(video['views'])
        videoCount += 1
        uniqueVideoCount += 1*(not video['duplicate'])
    return {"totalViews": totalViews, "videoCount": videoCount, "uniqueVideoCount": uniqueVideoCount, "videos": videos}

def tt_update():
    with open("views/tt_views.json") as f:
        json_data = json.load(f)
        videos = json_data['videos']
    updatedJson = getTotals(videos)
    with open("views/tt_views.json", "w") as f:
        json.dump(updatedJson, f, indent=4)

tt_update()
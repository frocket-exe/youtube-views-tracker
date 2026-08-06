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

def ig_update():
    with open("views/ig_views.json") as f:
        json_data = json.load(f)
        videos = json_data['videos']
    updatedJson = getTotals(videos)
    with open("views/ig_views.json", "w") as f:
        json.dump(updatedJson, f, indent=4)

ig_update()
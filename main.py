import json
from datetime import datetime

DOWNTIME_MINTIME = 120 #120m = 2h
MAX_UPCOMING_TIME = 120 #120m = 2h
UPDATE_CODES = {
    "MILESTONE_COMPLETE": 101,
    "MILESTONE_UPCOMING": 102,
    "SERVER_DOWN": 202
}

'''
1. Get YouTube videos from playlist
2. Calculates vps
3. Updates vps history
4. Prints:
    - Total views across x number of videos as of [time]
    - Number of views in number of seconds, vps
    - Checks if server has been down for 2 hours
    - VPS history, sorted VPS history, calc VPS
    - Views in the year, average year wide vps
    - Milestones hit, time to hit different milestones
    - How many views by the end of the year
5. Checks if server has been down for 2 hours - sends email
6. If new year, update year views . json
7. Email about upcoming milestones
8. Email about surpassed milestones
9. Update milestone json if necessary (maybe put milestone achievement dates in here?)
10. Track how many tokens are used in a day so I don't go over limit
11. Put variables which could change at top of page
'''

def calcTotals():
    """
    Adds total views, video count and vps from the other jsons.
    Writes to file and returns dictionary
    """
    with open("views/yt_views.json") as f:
        json_data = json.load(f)
        ytViews = json_data['totalViews']
        ytVideoCount = json_data['videoCount']
        calcVPS = json_data['calcVPS']
    with open("views/yt-short_views.json") as f:
        json_data = json.load(f)
        ytShortViews = json_data['totalViews']
        ytShortVideoCount = json_data['videoCount']
    with open("views/ig_views.json") as f:
        json_data = json.load(f)
        igViews = json_data['totalViews']
        igVideoCount = json_data['uniqueVideoCount']
    with open("views/tt_views.json") as f:
        json_data = json.load(f)
        ttViews = json_data['totalViews']
        ttVideoCount = json_data['uniqueVideoCount']
    totalViews = ytViews + ytShortViews + igViews + ttViews
    totalVideoCount = ytVideoCount + ytShortVideoCount + igVideoCount + ttVideoCount
    timestamp = int(datetime.now().timestamp())
    vps = calcVPS
    totals = {"totalViews": totalViews, "totalVideoCount": totalVideoCount, "timestamp": timestamp, "vps": vps}
    with open("views/total_views.json", "w") as f:
        json.dump(totals, f, indent=4)
    return(totals)

def main():
    # Update YouTube views
    # Update Instagram views
    # Update TikTok views
    totals = calcTotals()
    # Check server downtime
    # Check milestones
    # Check new year
    # Print totals
    # Print estimations

main()
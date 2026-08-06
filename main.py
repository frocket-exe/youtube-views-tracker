import json
from datetime import datetime
from update_yt import yt_update
from update_ig import ig_update
from update_tt import tt_update

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
        ytCalcVPS = json_data['calcVPS']
    with open("views/yt-short_views.json") as f:
        json_data = json.load(f)
        ytShortViews = json_data['totalViews']
        ytShortVideoCount = json_data['videoCount']
        ytShortCalcVPS = json_data['calcVPS']
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
    vps = ytCalcVPS + ytShortCalcVPS
    totals = {"totalViews": totalViews, "totalVideoCount": totalVideoCount, "timestamp": timestamp, "vps": vps}
    with open("views/total_views.json") as f:
        prevTime = json.load(f)['timestamp']
    with open("views/total_views.json", "w") as f:
        json.dump(totals, f, indent=4)
    totals['prevTime'] = prevTime
    return(totals)


def checkDowntime(totals):
    secondsSinceUpdate = totals['timestamp'] - totals['prevTime']
    minutesSinceUpdate = secondsSinceUpdate/60
    if minutesSinceUpdate > DOWNTIME_MINTIME:
        # Send downtime email
        print(f"Server has been down for {round(minutesSinceUpdate)}m!!!")
    else:
        print(f"\nLast update {round(minutesSinceUpdate)}m ago")


def checkMilestones(totals):
    totalViews = totals['totalViews']
    with open("viewData/milestones.json") as f:
        json_data = json.load(f)
        pastMilestones = json_data['past']
        milestones = json_data['future']
    nextMilestone = milestones[0]
    milestoneAchieved = (nextMilestone < totalViews)
    if milestoneAchieved:
        excessViews = totalViews - nextMilestone
        secondsSinceMilestone = round(excessViews/totals['vps'])
        timeAchieved = totals['timestamp'] - secondsSinceMilestone
        timeAchieved = datetime.strftime(datetime.fromtimestamp(timeAchieved), "%d/%m/%Y  %H:%M")
        print(f"{nextMilestone:,} achieved at {timeAchieved}")
        pastMilestones.update({f"{nextMilestone:,}": timeAchieved})
        milestones.remove(nextMilestone)
        with open("milestones.json", "w") as f:
            json.dump({"past": pastMilestones, "future":milestones}, f, indent=4)
        #SEND EMAIL
        if len(milestones=2):
            print("ONLY 2 FUTURE MILESTONES LEFT")
            #SEND EMAIL
    else:
        neededViews = nextMilestone - totalViews
        neededSeconds = round(neededViews/totals['vps'])
        neededMinutes = neededSeconds/60
        if neededMinutes <= MAX_UPCOMING_TIME:
            timeAchieved = totals['timestamp'] + neededSeconds
            timeUntil = datetime.strftime(datetime.fromtimestamp(neededSeconds), "%H:%M:%S")
            timeAchieved = datetime.strftime(datetime.fromtimestamp(timeAchieved), "%d/%m/%Y %H:%M")
            print(f"{nextMilestone:,} will be achieved at {timeAchieved} (in {timeUntil})")
            #SEND EMAIL



def estimations(totals):
    timestamp = totals['timestamp']
    currentYear = datetime.today().year
    with open("viewData/yearStartViews.json") as f:
        yearViews = json.load(f)
        yearStartViews = yearViews[str(currentYear)]
    currentViews = totals['totalViews']
    viewsThisYear = currentViews - yearStartViews
    secondsThisYear = timestamp - int(datetime.strptime(f"01/01/{currentYear}", "%d/%m/%Y").timestamp())
    yearMeanVPS = round((viewsThisYear/secondsThisYear), 5)
    secondsUntilYearEnd = int(datetime.strptime(f"31/12/{currentYear} 23:59:59", "%d/%m/%Y %H:%M:%S").timestamp()) - timestamp
    yearEndViews = currentViews + (secondsUntilYearEnd*yearMeanVPS)
    print(f"\n{yearMeanVPS} views per second mean")
    print(f"{round(yearMeanVPS*86400):,} views per day mean")
    print(f"{round(yearEndViews):,} views by end of the year\n")
    with open("viewData/milestones.json") as f:
        milestones = json.load(f)
        futureMilestones = milestones['future']
    print("Upcoming milestones:")
    for milestone in futureMilestones:
        print(f"{milestone:,}", end=" - ")
        viewsUntilAchieved = milestone - currentViews
        secondsUntilAchieved = round(viewsUntilAchieved/yearMeanVPS)
        timestampAchieved = timestamp + secondsUntilAchieved
        dateAchieved = datetime.fromtimestamp(timestampAchieved)
        print(datetime.strftime(dateAchieved, "%d/%m/%Y  %H:%M:%S"))
    
    

def main():
    # yt_update()
    # ig_update()
    # tt_update()
    totals = calcTotals()
    print(f"{totals["totalViews"]:,} views\nacross {totals["totalVideoCount"]:,} videos")
    checkDowntime(totals)
    checkMilestones(totals)
    # Check new year
    estimations(totals)

main()
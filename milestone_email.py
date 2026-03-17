def send_email(achieved, milestone, time):
    if achieved:
        emailBody = (f"\nYou achieved {milestone:,} views on {time}\n")
        emailSubject = (f"Achieved milestone - {milestone:,}")
    else:
        emailBody = (f"\nYou will achieve {milestone:,} views in {time} minutes\n")
        emailSubject = (f"Upcoming milestone - {milestone:,}")
    print(emailSubject)
    print(emailBody)

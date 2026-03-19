def email(achieved, milestone, time):
    senderEmail = os.getenv("SEND_EMAIL")
    loginEmail = os.getenv("LOGIN_EMAIL")
    senderPassword = os.getenv("SEND_PW")
    receiverEmail = os.getenv("RECEIVE_EMAIL")

    if achieved:
        emailBody = (f"\nYou achieved {milestone:,} views on {time}\n")
        emailSubject = (f"Achieved milestone - {milestone:,}")
    else:
        emailBody = (f"\nYou will achieve {milestone:,} views in {time} minutes\n")
        emailSubject = (f"Upcoming milestone - {milestone:,}")
        
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(loginEmail, senderPassword)
    message = (f"Subject: {emailSubject}\n\n{emailBody}")
    s.sendmail(senderEmail, receiverEmail, message)
    s.quit()

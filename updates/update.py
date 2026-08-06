import os
import smtplib

def email(emailSubject, emailBody):
    senderEmail = os.getenv("SEND_EMAIL")
    loginEmail = os.getenv("LOGIN_EMAIL")
    senderPassword = os.getenv("SEND_PW")
    receiverEmail = os.getenv("RECEIVE_EMAIL")
        
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(loginEmail, senderPassword)
    message = (f"Subject: {emailSubject}\n\n{emailBody}")
    s.sendmail(senderEmail, receiverEmail, message)
    s.quit()

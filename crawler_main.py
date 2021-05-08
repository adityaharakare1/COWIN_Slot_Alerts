import json
import requests
import datetime
import time
from playsound import playsound
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# Refresh once every 5 secs
REFRESH_FREQ = 5


def send_email(user_name, email_id, center, center_session):
    # Enter sender email details here
    sender_email = ""
    password = ""
    receiver_email = email_id

    message = MIMEMultipart("alternative")
    message["Subject"] = "Vaccination Slot Available"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the HTML version of your message
    html = """\
    <html>
      <body>
        <p>Hi {name},<br>
           The following vaccination slots are currently available:<br>
           <b>Center Name: {c_name}</b><br>
           Date: {date}<br>
           Fee Type: {fee_type}<br>
           Age Limit: {age_limit}<br>
           Vaccine: {vaccine}<br>
           Available Capacity: <b>{avail_cap}</b><br>
           <a href="https://www.cowin.gov.in/">Book your slots here</a> <br>
        </p>
        <p>
           Thanks and Regards, <br>
           COWIN Slot Alerts Harakare
        </p>
      </body>
    </html>
    """.format(name=user_name, c_name=center['name'], date=center_session['date'], fee_type=center['fee_type'],
               age_limit=center_session['min_age_limit'], vaccine=center_session['vaccine'],
               avail_cap=center_session['available_capacity'])

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(html, "html")
    message.attach(part1)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    print("Email sent")


def raise_alerts(user_name, email_id, center, center_session):
    print("Timestamp: ", datetime.datetime.now())
    print("FOUND AVAILABLE SLOT!!")
    print("Center Name: ", center['name'])
    print("Fee Type: ", center['fee_type'])
    print("Date: ", center_session['date'])
    print("Age Limit: ", center_session['min_age_limit'])
    print("Vaccine: ", center_session['vaccine'])
    print("Available Capacity: ", center_session['available_capacity'], "\n")
    send_email(user_name, email_id, center, center_session)
    playsound('alarm-buzzer.wav')
    playsound('alarm-buzzer.wav')


print("Welcome to COWIN Slot Alerts - Harakare")
print("---------------- USER DETAILS ----------------")
user_name = input("Enter your name: ")
email_id = input("Enter your email-id: ")
# mobile_no = input("Enter your mobile number: ")
user_age = input("Enter your age: ")

pincodes_ip = input("Comma separated Pincode(s): ")
pincodes_ip = pincodes_ip.replace(" ", "")
pincodes = pincodes_ip.split(",")

date_today = datetime.datetime.today()
date_today = date_today.strftime("%d-%m-%Y")
# pincode = "411001"
# date_today = "08-05-2021"
headers = {
    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"21b-u2yY89oK+gxUXxN9s7C4LbtuWas"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}
all_centers = []
print("----------------------------------------------")
for pincode in pincodes:
    try:
        url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=" + pincode + "&date=" + date_today
        response = requests.request("GET", url, headers=headers)
        # print(url)
        # print(response.text)
        json_response = json.loads(response.text)
        all_centers.extend(json_response['centers'])
    except:
        print("Pincode " + pincode + " ignored")
if len(all_centers) == 0:
    print("No centers found")
    time.sleep(5)
    sys.exit()

print("Following vaccination centers were found: ")
for center in all_centers:
    print(center['name'])
print("----------------------------------------------")
print("Filter 1 center using center name (Optional)")
print("Press Enter to select all")
selected_center = input("Enter the center name(eg: Sasoon): ")
filter_center = True
if selected_center is "":
    print("All centers selected")
    filter_center = False
for center in all_centers:
    if (selected_center.lower() in center['name'].lower()) and filter_center:
        print("Your selection: ")
        print("Center Name: ", center['name'])
        print("Center Address: ", center['address'])

print("-------------CURRENT AVAILABILITY-------------")
if filter_center:
    for center in all_centers:
        if selected_center.lower() in center['name'].lower():
            print("Fee Type: ", center['fee_type'])
            for center_session in center['sessions']:
                print("Date: ", center_session['date'])
                print("Age Limit: ", center_session['min_age_limit'])
                print("Vaccine: ", center_session['vaccine'])
                print("Available Capacity: ", center_session['available_capacity'], "\n")
else:
    for center in all_centers:
        print("Center Name: ", center['name'])
        print("Fee Type: ", center['fee_type'])
        for center_session in center['sessions']:
            print("Date: ", center_session['date'])
            print("Age Limit: ", center_session['min_age_limit'])
            print("Vaccine: ", center_session['vaccine'])
            print("Available Capacity: ", center_session['available_capacity'], "\n")
        print("----------------------------------------------")
print("----------------------------------------------")

while 1:
    print("1. Initialize Alerts when slots are available")
    print("2. Test Alarm Sound")
    print("3. Exit")
    usr_choice = input("Your choice(1/2/3): ")
    if usr_choice == "3":
        break
    elif usr_choice == "2":
        print("Ensure you can hear the alarm")
        playsound('alarm-buzzer.wav')
        print("----------------------------------------------")
    else:
        print("Alerts initialized")
        print("Do not close this window...")
        print("----------------------------------------------")
        slot_found = False
        while 1:
            # Update all_centers
            try:
                all_centers = []
                for pincode in pincodes:
                    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=" + pincode + "&date=" + date_today
                    response = requests.request("GET", url, headers=headers)
                    json_response = json.loads(response.text)
                    all_centers.extend(json_response['centers'])

                # Check if any session of selected center is available
                if filter_center:
                    for center in all_centers:
                        if selected_center.lower() in center['name'].lower():
                            for center_session in center['sessions']:
                                if (center_session['available_capacity'] != 0) and (
                                        int(user_age) >= center_session['min_age_limit']):
                                    raise_alerts(user_name, email_id, center, center_session)
                                    slot_found = True
                else:
                    for center in all_centers:
                        for center_session in center['sessions']:
                            if (center_session['available_capacity'] != 0) and (
                                    int(user_age) >= center_session['min_age_limit']):
                                raise_alerts(user_name, email_id, center, center_session)
                                slot_found = True
                time.sleep(5)
                if slot_found:
                    break
            except:
                print("Unexpected Error Occured. Closing Window...")
                time.sleep(5)
                sys.exit()

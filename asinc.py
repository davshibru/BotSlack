import schedule
import time
from threading import Thread

def job():
    print("I'm working...")

def jj():
    print("sec fun")

schedule.every(10).seconds.do(job)
schedule.every(20).seconds.do(jj)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every(5).to(10).minutes.do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().minute.at(":17").do(job)
def sleepme():
    while 1:
        schedule.run_pending()
        time.sleep(1)

while True:
    schedule.run_pending()
    time.sleep(1)



th = Thread(target=sleepme)
th.start()

for i in range(1000):
    num = int(input('введите число - '))
    print(i + num)


#import datetime

#import time
#time settings
#today_var = datetime.date.today() #+ datetime.timedelta(days=1)
# scheduled_time = datetime.time(hour=13, minute=58)
# schedule_timestamp = (datetime.datetime.combine(tomorrow, scheduled_time) + datetime.timedelta(seconds=0)).timestamp()

#REPORTS[today_var.strftime("%Y:%m:%d")] = {}
#print(REPORTS)
import sys
import json
import requests
import time
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

# for enabling and disabling the subs to view shit which is outed and not valid anymore
THEORETICAL_VIEWS = False

# from colorama import init
# from colorama import Fore, Style
# init()

## TODO Add in share differences
## TODO Modify % to * 100
HOLO_POI_URL = "https://holo.poi.cat/api/v4/channels_report?ids={holo}&metrics=youtube_channel_subscriber,youtube_channel_view&startAt={startDate}&endAt={endDate}"
NASFAQ_URL = "https://nasfaq.biz/api/getStats"



# subs are possibly worth about 10k view for 1k subs
# this doesn't apply anymore but I'm too lazy to scrub it out
SUB_TO_VIEW_VALUE = 10000

# list the holos by their generation according to nasfaq since
# the lists returned by neither server does so
HOLOS = ["hololive", "sora", "roboco", "miko", "suisei", "azki", "mel", "fubuki", "matsuri", "aki", "haato", "aqua", "shion", "ayame", "choco", "choco_alt", "subaru", "mio", "okayu", "korone", "pekora", "rushia", "flare", "noel", "marine", "kanata", "coco", "watame", "towa", "himemoriluna", "lamy", "nene", "botan", "polka", "risu", "moona", "iofi", "calliope", "kiara", "inanis", "gura", "amelia", "ollie", "melfissa", "reine", "ui", "nana", "pochimaru", "ayamy", "civia"]

# need to ensure we dont get fucked by dumb time fuckery which includes dst
TIMEZONE = ZoneInfo("Australia/Brisbane")
#values for when adjustments occurs
LOCAL_RESET_HOUR = 15
#nasfaq
LOCAL_ADJUSTMENT_MINUTE = 5
#this is for holopoi
LOCAL_RESET_MINUTE = 0


# testHolo = "kanata"

# with open("data_file.json", "w") as write_file:
#     json.dump(data, write_file)
currentTime = int(time.time() * 1e3) 
threeDaysMilliSeconds = 259200000

threeDaysAgoTime = int((currentTime - threeDaysMilliSeconds))
# testHolo = "kanata"
# testHoloURL = HOLO_POI_URL.format(holo=testHolo, startDate=threeDaysAgoTime, endDate=currentTime)
# print(testHoloURL)
# response = requests.get(testHoloURL)

statResponse = requests.get(NASFAQ_URL)
coinHistory = json.loads(statResponse.json()['coinHistory'])

currentDate = datetime.now()
dateFormat = "{month}/{day}/{year}"

currentDateStamp = dateFormat.format(month = currentDate.strftime("%m"), day = currentDate.strftime("%d"), year = currentDate.strftime("%Y"))

holoList = statResponse.json()['stats']
poiStatCount ={}

yesterdayAdjustmentTime = coinHistory[-1]['timestamp']
# for tick in reversed(range(len(statResponse.json()['coinInfo']['data']['aki']['history']))):
#     pass
#     curTimestamp = statResponse.json()['coinInfo']['data']['aki']['history'][tick]['timestamp']
#     curDate = datetime.fromtimestamp(curTimestamp / 1e3).replace(tzinfo=TIMEZONE)
#     curHour = curDate.hour
#     curMinute = curDate.minute
#     if (curHour == LOCAL_RESET_HOUR and LOCAL_ADJUSTMENT_MINUTE == curDate.minute and LOCAL_ADJUSTMENT_MINUTE == (curDate.minute - 1) and LOCAL_ADJUSTMENT_MINUTE == (curDate.minute + 1) ):
#         yesterdayAdjustmentTime = curTimestamp

yesterdayAdjustmentHistory = {}

# for holo in statResponse.json()['coinInfo']['data']:
#     pass
#     history = statResponse.json()['coinInfo']['data'][holo]['history']
#     for tick in reversed(range(len(history))):
#         if(history[tick]['timestamp'] == yesterdayAdjustmentTime):
#             pass
#             yesterdayAdjustmentHistory[holo] = history[tick]
for tick in reversed(range(len(coinHistory))):
    pass
    history = coinHistory
    if(history[tick]['timestamp'] == yesterdayAdjustmentTime):
        pass
        yesterdayAdjustmentHistory = history[tick]['data']
todayCoinHistory = {}
for holo in statResponse.json()['coinInfo']['data']:
    pass
    todayCoinHistory[holo] = statResponse.json()['coinInfo']['data'][holo]

# todayCoinHistory = statResponse.json()['todayPrices'][-1]["coinInfo"]['data']




for holo in HOLOS:
    if (holo == 'civia'):
        continue
    holoPoiUrl = HOLO_POI_URL.format(holo=holo, startDate=threeDaysAgoTime, endDate=currentTime)
    poiStatReponse = requests.get(holoPoiUrl)
    # print(poiStatReponse.json())
    nasDailySubCount = holoList[holo]['dailySubscriberCount']['data'][-1]
    nasDailyViewCount = holoList[holo]['dailyViewCount']['data'][-1]

    holoPoiStatCount = {}

    yesterday = currentDate - timedelta(days=1)
    twoDaysAgo = currentDate - timedelta(days=2)

    for report in poiStatReponse.json()['reports']:
        pass
        # print(report)
        # print('\n\n\n\n')
        rows = report['rows']
        poiTodayCount = {"time":rows[-1][0], "value":rows[-1][1]}
        poiYesterdayCount = {}
        poiTwoDaysCount ={}
        poiDailyCount = 0

        statCounts = {}
        statCounts['today'] = poiTodayCount

        for row in reversed(range(len(rows)-1)):
            pass
            time = rows[row][0]
            unixTime = time/1e3
            # print(unixTime)
            date = datetime.fromtimestamp(unixTime).replace(tzinfo=TIMEZONE)
            day = date.day
            hour = date.hour
            minutes = date.minute
            # print(date)
            # print(day == yesterday.day)
            # print(hour == LOCAL_RESET_HOUR)
            # print(minutes == LOCAL_RESET_MINUTE)
            if (day == yesterday.day and hour == LOCAL_RESET_HOUR and minutes == LOCAL_RESET_MINUTE):
                poiYesterdayCount = {"time":rows[row][0], "value":rows[row][1]}
                statCounts['yesterday'] = poiYesterdayCount

            elif(day == twoDaysAgo.day and hour == LOCAL_RESET_HOUR and minutes == LOCAL_RESET_MINUTE):
                poiTwoDaysCount = {"time":rows[row][0], "value":rows[row][1]}
                statCounts['twoDays'] = poiTwoDaysCount

        if (report['kind'] == "youtube_channel_subscriber"):
            pass
            holoPoiStatCount['subs'] = statCounts
        elif (report['kind'] == 'youtube_channel_view'):
            pass
            holoPoiStatCount['views'] = statCounts
    poiStatCount[holo] = holoPoiStatCount
    # break

with open('holostats.txt', 'w') as statFile:

    def PrintStats(holo):
        holoPoiStatCount = poiStatCount[holo]

        todayViews = holoPoiStatCount['views']['today']['value']
        yesterdayViews = holoPoiStatCount['views']['yesterday']['value']
        twoDaysViews = holoPoiStatCount['views']['twoDays']['value']

        todaySubs = holoPoiStatCount['subs']['today']['value']
        yesterdaySubs = holoPoiStatCount['subs']['yesterday']['value']
        twoDaysSubs = holoPoiStatCount['subs']['twoDays']['value']

        dailyViewDifference = todayViews - yesterdayViews
        yesterdayViewDifference = yesterdayViews - twoDaysViews
        dailySubDifference = todaySubs - yesterdaySubs
        yesterdaySubDifference = yesterdaySubs - twoDaysSubs

        theoreticalSubViews = 0
        theoreticalYesterdaySubViews = 0
        if(dailySubDifference / 1000 != 0):
            theoreticalSubViews = (dailySubDifference / 1000) * SUB_TO_VIEW_VALUE
        if(yesterdaySubDifference / 1000 != 0):
            theoreticalYesterdaySubViews = (yesterdaySubDifference / 1000) * SUB_TO_VIEW_VALUE


        # print(todayViews)
        # print(yesterdayViews)
        # print(dailyViewDifference)

        # print (Fore.BLUE)

        print(holo)

        # print(Style.RESET_ALL)

        holoPoiStatCount=poiStatCount[holo]

        if(holo == "choco"):
            todayViews += poiStatCount['choco_alt']['views']['today']['value']
            yesterdayViews += poiStatCount['choco_alt']['views']['yesterday']['value']
            todaySubs += poiStatCount['choco_alt']['views']['today']['value']
            yesterdaySubs += poiStatCount['choco_alt']['views']['yesterday']['value']

        print("Today views - {views}".format(views=todayViews))
        print("Yesterday views - {views}".format(views=yesterdayViews))
        print("Daily difference - {difference}".format(difference=(dailyViewDifference)))
        print("Yesterday daily difference - {difference}".format(difference=(yesterdayViewDifference)))
        print("Day difference - {difference}".format(difference=(dailyViewDifference - yesterdayViewDifference)))
        if(dailyViewDifference != 0):
            if(yesterdayViewDifference != 0):
                print("Daily % difference - {difference}%".format(difference=((float(dailyViewDifference / yesterdayViewDifference) -1) * 100)))

        if(THEORETICAL_VIEWS):
            print("Theoretical daily views with sub views - {views}".format(views=((dailyViewDifference) + theoreticalSubViews)))
            print("Theoretical yesterday daily views with sub views - {views}".format(views=((yesterdayViewDifference) + theoreticalYesterdaySubViews)))
            print("Daily difference with theoretical views - {difference}".format(difference=((dailyViewDifference + theoreticalSubViews) - (yesterdayViewDifference + theoreticalYesterdaySubViews))))
            if(yesterdayViewDifference != 0 and theoreticalYesterdaySubViews != 0):
                print("Daily % difference with theoretical views - {difference}".format(difference=(((float(dailyViewDifference + theoreticalSubViews) / (yesterdayViewDifference + theoreticalYesterdaySubViews)) -1) * 100)))

        print("\nToday coin circulation - {circulated}".format(circulated=todayCoinHistory[holo]['inCirculation']))
        print("Yesterday coin circulation - {circulated}".format(circulated=yesterdayAdjustmentHistory[holo]['inCirculation']))
        print("Daily coin circulation difference - {circulated}".format(circulated=todayCoinHistory[holo]['inCirculation'] - yesterdayAdjustmentHistory[holo]['inCirculation']))
        print("Daily coin % circulation difference - {circulated}%".format(circulated=((todayCoinHistory[holo]['inCirculation'] / yesterdayAdjustmentHistory[holo]['inCirculation']) -1) * 100))







        print("\nToday subs - {views}".format(views=todaySubs))
        print("Yesterday subs - {views}".format(views=yesterdaySubs))
        print("Daily difference - {difference}".format(difference=(dailySubDifference)))
        print("Yesterday daily difference - {difference}".format(difference=(yesterdaySubDifference)))
        if(dailySubDifference != 0):
            if(yesterdaySubDifference != 0):
                print("Daily % difference - {difference}%".format(difference=((float(dailySubDifference / yesterdaySubDifference) - 1) * 100)))

        print ("\n---------------------------------")


    for holo in poiStatCount:
        if(holo =="choco_alt"):
            continue
        PrintStats(holo)
        orgStdout = sys.stdout
        sys.stdout = statFile
        PrintStats(holo)
        sys.stdout = orgStdout

import sys
import json
import requests
import time
import datetime
import csv


# from colorama import init
# from colorama import Fore, Style
# init()


HOLO_DIVS_URL = "https://nasfaq.biz/api/getDividends"
HOLO_STATS_URL = "https://nasfaq.biz/api/getStats"

SEVENTEEN_HOURS = 61200

HOLOS = ["hololive", "sora", "roboco", "miko", "suisei", "azki", "mel", "fubuki", "matsuri", "aki", "haato", "aqua", "shion", "ayame", "choco", "choco_alt", "subaru", "mio", "okayu", "korone", "pekora", "rushia", "flare", "noel", "marine", "kanata", "coco", "watame", "towa", "himemoriluna", "lamy", "nene", "botan", "polka", "risu", "moona", "iofi", "calliope", "kiara", "inanis", "gura", "amelia", "ollie", "melfissa", "reine", "ui", "nana", "pochimaru", "ayamy", "civia"]
HOLOS = ["hololive", "sora", "roboco", "miko", "suisei", "azki", "mel", "fubuki", "matsuri", "aki", "haato", "aqua", "shion", "ayame", "choco", "choco_alt", "subaru", "mio", "okayu", "korone", "pekora", "rushia", "flare", "noel", "marine", "kanata", "coco", "watame", "towa", "himemoriluna", "lamy", "nene", "botan", "polka", "risu", "moona", "iofi", "calliope", "kiara", "inanis", "gura", "amelia", "ollie", "melfissa", "reine", "ui", "nana", "civia"]




divResponse = requests.get(HOLO_DIVS_URL)
statResponse =requests.get(HOLO_STATS_URL)

# with open("data_file.json", "w") as write_file:
#     json.dump(data, write_file)

# currentTime = int(time.time())

currentDate = datetime.datetime.now()

lastFriday = (currentDate.date() - datetime.timedelta(days=currentDate.weekday()) + datetime.timedelta(days=4, weeks=-1))


divsList = divResponse.json()['dividends']['payouts']
holoStats = statResponse.json()['stats']

dateFormat = "{month}/{day}/{year}"
lastFridayDateStamp = dateFormat.format(month = lastFriday.strftime("%m"), day = lastFriday.strftime("%d"), year = lastFriday.strftime("%Y"))
currentDateStamp = dateFormat.format(month = currentDate.strftime("%m"), day = currentDate.strftime("%d"), year = currentDate.strftime("%Y"))

# divs
divs = {}
with open("holodivs.json", "r+") as jsonFile:
    divs = json.load(jsonFile)
    curDivTime = int(divResponse.json()['dividends']['timestamp'])

    if str(curDivTime) in divs:
        pass
    else:
        divs[curDivTime] = divsList
        jsonFile.seek(0)
        json.dump(divs, jsonFile)
lastWeekDivTime = 0
for divTime in divs:
    if(int(divTime) > time.mktime(lastFriday.timetuple()) + SEVENTEEN_HOURS):
        lastWeekDivTime = divTime
lastWeekDivs = divs[lastWeekDivTime]


# current prices
# todayPrices = statResponse.json()['todayPrices'][-1]['coinInfo']['data']
todayPrices = {}
for holo in statResponse.json()['coinInfo']['data']:
    pass
    todayPrices[holo] = statResponse.json()['coinInfo']['data'][holo]


goodHolos = {}
acceptableHolos= {}
with open("holodivs.txt", "w") as holoDivFile:

    for holo in HOLOS:
        if (holo == 'civia' or holo == "choco_alt"):
            continue
        divPayout = 0
        if (holo in divsList.keys()):
            divPayout = divsList[holo]

        prevFridayIndex = 0
        curDateIndex = 0

        weeklyViewStats = holoStats[holo]['weeklyViewCount']
        weeklySubsStats = holoStats[holo]['weeklySubscriberCount']
        dateLabels = weeklyViewStats['labels']

        for date in range(len(dateLabels)):
            if (dateLabels[date] == lastFridayDateStamp):
                prevFridayIndex = date
            elif (dateLabels[date] == currentDateStamp):
                curDateIndex = int(date)

        prevFridayWeeklyViews = int(weeklyViewStats['data'][prevFridayIndex])
        curWeeklyViews = int(weeklyViewStats['data'][curDateIndex])

        prevFridayWeeklySubs = int(weeklySubsStats['data'][prevFridayIndex])
        curWeeklySubs = int(weeklySubsStats['data'][curDateIndex])
        if (holo == "choco"):
            pass
            chocoAlt = holoStats['choco_alt']
            prevFridayWeeklyViews += int(chocoAlt['weeklyViewCount']['data'][prevFridayIndex])
            curWeeklyViews += int(chocoAlt['weeklyViewCount']['data'][curDateIndex])

            prevFridayWeeklySubs += int(chocoAlt['weeklySubscriberCount']['data'][prevFridayIndex])
            curWeeklySubs += int(chocoAlt['weeklySubscriberCount']['data'][curDateIndex])


        if (lastWeekDivs[holo] / todayPrices[holo]['price'] >= 0.30):
            pass
            normDiv = (lastWeekDivs[holo] / todayPrices[holo]['price'])
            div10 = (lastWeekDivs[holo] * 1.1) / todayPrices[holo]['price']
            goodHolos[holo] = {"div": normDiv, "div10": div10,"price":lastWeekDivs[holo]}
        elif ((lastWeekDivs[holo] * 1.1) / todayPrices[holo]['price'] >= 0.30):
            pass
            normDiv = (lastWeekDivs[holo] / todayPrices[holo]['price'])
            div10 = (lastWeekDivs[holo] * 1.1) / todayPrices[holo]['price']
            acceptableHolos[holo] = {"div": normDiv, "div10": div10,"price":lastWeekDivs[holo]}

        def PrintStats():
            # print (Fore.BLUE)

            print(holo)

            # print(Style.RESET_ALL)

            print ( "\nPF views - " + str(prevFridayWeeklyViews))
            print ( "CW views - " + str(curWeeklyViews))
            print ("View count difference - " + str(curWeeklyViews - prevFridayWeeklyViews))
            print ("Views % difference - " + str(((curWeeklyViews / prevFridayWeeklyViews) - 1) * 100) + "%\n")

            print ( "PF subs - " + str(prevFridayWeeklySubs))
            print ( "CW subs - " + str(curWeeklySubs))
            print ("Subs count difference - " + str(curWeeklyViews - prevFridayWeeklySubs))
            if (curWeeklySubs != 0):
                print ("Subs % difference - " + str(((curWeeklySubs / prevFridayWeeklySubs) - 1) * 100)+ "%\n")

            print ("Last week divs - " + str(lastWeekDivs[holo]))
            # print(Fore.GREEN)
            print ( "Div/coin price - " + str(lastWeekDivs[holo] / todayPrices[holo]['price'] ))

            # print(Style.RESET_ALL)

            print ("+10% div/last week - " + str(lastWeekDivs[holo] * 1.1))
            # print(Fore.RED)
            print (("+10% div/coin price - " + str((lastWeekDivs[holo] * 1.1) / todayPrices[holo]['price'])))
            
            # print(Style.RESET_ALL)

            print("\n--------------------------------------\n")

        PrintStats()
        orgStdout = sys.stdout
        sys.stdout = holoDivFile
        PrintStats()
        sys.stdout = orgStdout

    def PrintGoodHolos(holo):
        div = goodHolos[holo]['div']
        div10 = goodHolos[holo]['div10']
        printStatement = "{holo} - div {div} - 10% {div10}".format(holo=holo, div=div, div10=div10)
        print(printStatement)
        print("Last week div price - {price}".format(price=goodHolos[holo]['price']))
        printStatement = "300k/current coin price/div - {totalDivCost}"
        totalDivCost = (300000/todayPrices[holo]['price']) * lastWeekDivs[holo]
        print(printStatement.format(totalDivCost=totalDivCost))

        printStatement = "300k/current coin price/10% div - {totalDivCost}\n"
        totalDivCost = (300000/todayPrices[holo]['price']) * (lastWeekDivs[holo] *1.1)
        print(printStatement.format(totalDivCost=totalDivCost))


    print("Good Holos\n")
    
    sys.stdout = holoDivFile
    print("Good Holos\n")
    sys.stdout = orgStdout

    # TODO Clean up the vars so its easier to read
    for holo in goodHolos:
        pass
        PrintGoodHolos(holo)
        orgStdout = sys.stdout
        sys.stdout = holoDivFile
        PrintGoodHolos(holo)
        sys.stdout = orgStdout


    print("\n--------------------------------------\n")


    print ("Acceptable Holos\n")
    sys.stdout = holoDivFile
    print ("Acceptable Holos\n")
    sys.stdout = orgStdout

    def PrintAcceptableHolos(holo):
        div = acceptableHolos[holo]['div']
        div10 = acceptableHolos[holo]['div10']
        printStatement = "{holo} - div {div} - 10% {div10}".format(holo=holo, div=div, div10=div10)
        print(printStatement)
        print("Last week div price - {price}".format(price=acceptableHolos[holo]['price']))
        printStatement = "300k/current coin price/div - {totalDivCost}"
        totalDivCost = (300000/todayPrices[holo]['price']) * lastWeekDivs[holo]
        print(printStatement.format(totalDivCost=totalDivCost))

        printStatement = "300k/current coin price/10% div - {totalDivCost}\n"
        totalDivCost = (300000/todayPrices[holo]['price']) * (lastWeekDivs[holo] *1.1)
        print(printStatement.format(totalDivCost=totalDivCost))


    for holo in acceptableHolos:
        pass
        PrintAcceptableHolos(holo)
        orgStdout = sys.stdout
        sys.stdout = holoDivFile
        PrintAcceptableHolos(holo)
        sys.stdout = orgStdout

# with open('output.csv', 'wb') as output:
#     writer = csv.writer(output)
#     for key, value in goodHolos.iteritems():
# #         writer.writerow([key, value])

# import openpyxl

# df= pd.DataFrame.from_dict(goodHolos, orient='index')
# df.to_excel(r"output.xlsx",sheet_name='Sheet_name')

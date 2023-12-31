__all__ = ["export"]
__author__ = "Toby Clark"

from time import sleep
from exportSpreadsheet import ExportSpreadsheets
from printing import Printing
from extractCourtData import get_court_data
from setupData import check_setup
from pathlib import Path
from datetime import datetime
import logging
import xlwings as xw


def makeExcel(day, exportLink, teamPlayerData, outputFolder):
    yearType = "kids"
    if day == "wednesday":
        yearType = "adults"

    p = Printing()

    p.print_new()
    data, date = get_court_data(teamPlayerData, exportLink)
    print(f"    {day} Web data extracted, now saving to excel templates")
    p.print_new()

    fp = outputFolder / f"{str(date)}-{day}-games.xlsx"
    export = ExportSpreadsheets(str(fp), yearType)

    p.print_inline("opened output and templates")

    export.add_data(data)
    p.print_new()

    export.save()

    print(f"{day} games saved to:\n{str(fp)}")


def killall():
    # Trying quitting gracefully
    for app in xw.apps.keys():
        xw.apps[app].quit()

    # Kill all excel processes
    for app in xw.apps.keys():
        print("Excel app still running with pid: ", app)
        xw.apps[app].kill()

    # Worst case set excel apps to visible to be closed manually
    if xw.apps.keys():
        for app in xw.apps.keys():
            xw.apps[app].visbile = True

        logging.fatal("Excel not cleaned up! All apps set to visible")
        raise Exception(
            "Excel not cleaned up! All apps set to visible")


def try_catch_fail(msg, kill=False):
    Printing().print_new()
    print(msg)

    if kill:
        sleep(3)
        killall()


def loggingConfig():
    logPath = Path(__file__).parent / "logs"
    logPath.mkdir(exist_ok=True, parents=True)

    logFormatter = logging.Formatter("[%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(
        "{0}/{1}.log".format(logPath, datetime.now().timestamp()))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)


def export():
    # TODO: get logging to work and save to file
    # loggingConfig()

    Printing().welcome()
    sundayYears = [["3/4", "https://www.nsbl.com.au/years-3-4"],
                   ["5/6", "https://www.nsbl.com.au/years-5-6"],
                   ["7/8", "https://www.nsbl.com.au/years-7-8"],
                   ["9-12", "https://www.nsbl.com.au/years-9"]
                   ]
    wednesdayGame = [["adults", "https://www.nsbl.com.au/adultcompetition"]]

    try:
        teamPlayerData, outputFolder = check_setup()
    except Exception as err:
        logging.fatal(err, err.args, err.with_traceback)
        try_catch_fail(f"    Error occured getting setup: {err}", True)
        return

    try:
        makeExcel("sunday", sundayYears, teamPlayerData, outputFolder)
    except Exception as err:
        logging.fatal(err, err.args, err.with_traceback)
        try_catch_fail(f"    Error occured getting sunday games {err}")

    try:
        makeExcel("wednesday", wednesdayGame, teamPlayerData, outputFolder)
    except Exception as err:
        logging.fatal(err, err.args, err.with_traceback)
        try_catch_fail(f"    Error occured getting Wednesday games {err}")

    killall()
    sleep(3)


if __name__ == "__main__":
    export()

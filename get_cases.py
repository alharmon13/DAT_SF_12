import datetime
import time
import json
import pprint
import desk_common as desk_util
from optparse import OptionParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

BASE_API_URL = "https://asana.desk.com"

def main(begin_episode, end_episode):
  begin_episode_ts = time.mktime(datetime.datetime.strptime(begin_episode, "%Y-%m-%d").timetuple())
  end_episode_ts = time.mktime(datetime.datetime.strptime(end_episode, "%Y-%m-%d").timetuple())

  channel = "email"
  status = "resolved,closed"
  per_page = 100
  desk = desk_util.connectToDesk()
  cases_list = getCases(desk, begin_episode_ts, end_episode_ts, channel, status, per_page)
  print cases_list


def getCases(desk, since_created_at, max_created_at, channel, status, per_page):
  cases_list = []
  payload = {
    "since_created_at" : since_created_at,
    "max_created_at" : max_created_at,
    "channel" : channel,
    "status" : status,
    "per_page" : per_page
  }
  cases = desk.get("https://asana.desk.com/api/v2/cases/search", params=payload)

  while cases:
    desk_util.avoidRateLimit(cases)
    cases_json = json.loads(cases.content)
    entries = (cases_json["_embedded"]["entries"])

    for entry in entries:
    	cases_list.append(entry)

    try:
      next_page_url = BASE_API_URL + cases_json["_links"]["next"]["href"]
      cases = desk.get(next_page_url)

    except TypeError:
      break
  return cases_list


if __name__ == "__main__":
  parser = OptionParser()

  parser.add_option("-f", "--from_date",
    dest="from_date",
    default=None,
    help="beginning of episode (YYYY-MM-DD)")

  parser.add_option("-t", "--to_date",
    dest="to_date",
    default=None,
    help="end of episode (YYYY-MM-DD)")

  (options, args) = parser.parse_args()

  if options.from_date is not None and options.to_date is not None:
    begin_episode = options.from_date
    end_episode = options.to_date
    main(begin_episode, end_episode)
  else:
    print "please provide start and end dates"
    exit(0)

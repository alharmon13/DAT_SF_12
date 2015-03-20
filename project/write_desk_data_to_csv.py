"""
Writes data from Desk cases (case ID, date created, time created, time first
resolved, and time to first response (TFR)) to a CSV file named desk_data.csv

"""

import time
import pytz
import json
import pprint
#import asana.stats.biz.uo.desk_common as desk
import desk_common as desk_util
from optparse import OptionParser
from time import mktime
from pytz import timezone
from datetime import timedelta, datetime
from dateutil import tz
import csv


BASE_API_URL = "https://asana.desk.com"

def main(begin_episode, end_episode):
  begin_episode_ts = time.mktime(datetime.strptime(begin_episode, "%Y-%m-%d").timetuple())
  end_episode_ts = time.mktime(datetime.strptime(end_episode, "%Y-%m-%d").timetuple())
  channel = "email"
  status = "resolved,closed"
  per_page = 100
  desk = desk_util.connectToDesk()
  case_ids, created_at_dates, created_at_times, first_resolved_at_times, raw_tfr = getDeskData(desk, begin_episode_ts, end_episode_ts, channel, status, per_page)
  writeDeskDataToCSV(case_ids, created_at_dates, created_at_times, first_resolved_at_times, raw_tfr)
  print "Make sure lengths match: ", len(case_ids), len(created_at_dates), len(created_at_times), len(first_resolved_at_times), len(raw_tfr)

def writeDeskDataToCSV(case_ids, created_at_dates, created_at_times, first_resolved_at_times, raw_tfr):
    rows = zip(case_ids, created_at_dates, created_at_times, first_resolved_at_times, raw_tfr)
    with open('desk_data.csv','wb') as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(row)

def getDeskData(desk, since_created_at, max_created_at, channel, status, per_page):
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
      case_ids = []
      created_at_times = []
      created_at_dates = []
      first_resolved_at_times = []
      raw_tfr = []
      for entry in entries:
          excluded_dates = ["2013-11-28", "2013-11-29", "2013-12-23", "2013-12-24", "2013-12-25",
                            "2013-12-31", "2013-12-30", "2014-02-17", "2014-05-26", "2014-07-04",
                            "2014-09-01","2014-11-27", "2014-11-28", "2014-12-24", "2014-12-25",
                            "2014-12-26", "2015-01-01", "2015-01-02"]
          specific_queues = ["/api/v2/groups/19411", "/api/v2/groups/82567", "/api/v2/groups/19412"]
          too_long = timedelta(days=4)
          if (entry["_links"]["assigned_group"] is not None and
            entry["created_at"] is not None and
            entry["first_resolved_at"] is not None):
              FROM_ZONE = tz.tzutc()
              SF_TZ = timezone("US/Pacific")
#convert created at times to SF
              created_at_1 = (datetime.strptime(entry["created_at"], '%Y-%m-%dT%H:%M:%SZ'))
              created_at_2 = (datetime.date(created_at_1))
              created_at_good_format = created_at_2.strftime('%Y-%m-%d')
              sf_time_created_at_1 = created_at_1.replace(tzinfo=FROM_ZONE)
              sf_time_created_at_2 = SF_TZ.normalize(sf_time_created_at_1.astimezone(SF_TZ))
              sf_created_time = (datetime.time(sf_time_created_at_2))
#convert resolve at times to SF
              resolved_at_1 = datetime.strptime(entry["first_resolved_at"],"%Y-%m-%dT%H:%M:%SZ")
              resolved_at_2 = (datetime.date(resolved_at_1))
              resolved_at_good_format = resolved_at_2.strftime('%Y-%m-%d')
              sf_time_resolved_at_1 = resolved_at_1.replace(tzinfo=FROM_ZONE)
              sf_time_resolved_at_2 = SF_TZ.normalize(sf_time_resolved_at_1.astimezone(SF_TZ))
              sf_resolved_at_time = (datetime.time(sf_time_resolved_at_2))
#create tfr timedelta
              time_delta = resolved_at_1 - created_at_1
#write to appropriate lists
              if (entry["_links"]["assigned_group"]["href"] in specific_queues and
                created_at_good_format not in excluded_dates and
                time_delta < too_long and
                entry["_links"]["replies"]["count"] > 0):
                    print "got here"
#write to appropriate lists
                    created_at_dates.append(created_at_good_format)
                    created_at_times.append(sf_created_time)
                    first_resolved_at_times.append(sf_resolved_at_time)
                    raw_tfr.append(time_delta)
                    case_ids.append(entry["id"])
#http://stackoverflow.com/questions/17704244/writing-python-lists-to-columns-in-csv
      try:
        next_page_url = BASE_API_URL + cases_json["_links"]["next"]["href"]
        cases = desk.get(next_page_url)

      except TypeError:
        break
#return lists
    return case_ids, created_at_dates, created_at_times, first_resolved_at_times, raw_tfr

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

#import datetime
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
  tfr_list, case_ids, num_cases = getCases(desk, begin_episode_ts, end_episode_ts, channel, status, per_page)
  writeDataToCSV(tfr_list, case_ids)
  avg_sum = sum(tfr_list, timedelta())
  avg_sum_h = (avg_sum.total_seconds())/3600
  list_len = len(tfr_list)
  average = float(avg_sum_h/list_len)
  print "Average =", average, ". Number of cases in closed hours:", num_cases

def writeDataToCSV(tfr_list, case_ids):
    rows = zip(case_ids, tfr_list)
    with open('tfr_desk_data.csv','wb') as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(row)

def getCases(desk, since_created_at, max_created_at, channel, status, per_page):
  tfr_list = []
  case_ids = []
  num_cases = 0
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
        excluded_dates = ["2013-11-28", "2013-11-29", "2013-12-23", "2013-12-24", "2013-12-25",
                          "2013-12-31", "2013-12-30", "2014-02-17", "2014-05-26", "2014-07-04",
                          "2014-09-01","2014-11-27", "2014-11-28", "2014-12-24", "2014-12-25",
                          "2014-12-26", "2015-01-01", "2015-01-02"]
        specific_queues = ["/api/v2/groups/19411", "/api/v2/groups/82567", "/api/v2/groups/19412"]
        too_long = timedelta(days=4)
        twelve_hours = timedelta(hours=12)
        eleven_hours = timedelta(hours=11)
        ten_hours = timedelta(hours=10)
        nine_hours = timedelta(hours=9)
        eight_hours = timedelta(hours=8)
        seven_hours = timedelta(hours=7)
        six_hours = timedelta(hours=6)
        five_hours = timedelta(hours=5)
        four_hours = timedelta(hours=4)
        three_hours = timedelta(hours=3)
        two_hours = timedelta(hours=2)
        one_hour = timedelta(hours=1)
        closed_hours = ["19", "20", "21", "22", "23", "0", "1", "2", "3", "4", "5", "6"]
        big_team_mean = timedelta(hours=1) ##change this
        premium_mean = timedelta(hours=4) ##change this
        free_mean = timedelta(hours=8) ##change this

        if (entry["_links"]["assigned_group"] is not None and
        entry["created_at"] is not None and
        entry["first_resolved_at"] is not None and
        entry["_links"]["assigned_group"]["href"] in specific_queues):
# put timestampts into a good format
            created_at_ts = datetime.strptime(entry["created_at"],"%Y-%m-%dT%H:%M:%SZ")
            resolved_at_ts = datetime.strptime(entry["first_resolved_at"],"%Y-%m-%dT%H:%M:%SZ")
            entryA = (datetime.strptime(entry["created_at"], '%Y-%m-%dT%H:%M:%SZ'))
            entryB = (datetime.date(entryA))
            entry_good_format = entryB.strftime('%Y-%m-%d')
            time_delta = resolved_at_ts - created_at_ts
# convert necessary times into PST
            FROM_ZONE = tz.tzutc()
            SF_TZ = timezone("US/Pacific")
            sf_time_ = entryA.replace(tzinfo=FROM_ZONE)
            sf_time = SF_TZ.normalize(sf_time_.astimezone(SF_TZ))
            time_ = (datetime.time(sf_time))
            time_good = str(time_.hour)
        else:
            continue
        if (time_delta > too_long or
         entry_good_format in excluded_dates):
               continue
        if time_good in closed_hours:
            num_cases += 1

# ------------- break down adjustment per hour -------------  #
        times_dict = {"19": six_hours, "20": five_hours, "21": four_hours, "22": three_hours, "23": two_hours, "0": one_hour}
        #import pdb;pdb.set_trace()
        if times_dict.has_key(time_good):
## BIG TEAMS ##
            if entry["custom_fields"]["big_team"] == True:
                if time_delta > times_dict[time_good] + big_team_mean:
                    new_time_delta = times_dict[time_good] + big_team_mean
                else:
                    new_time_delta = time_delta
## PREMIUM ##
            elif entry["custom_fields"]["priority_support"] == True:
                if time_delta > times_dict[time_good] + premium_mean:
                    new_time_delta = times_dict[time_good] + premium_mean
                else:
                    new_time_delta = time_delta
## FREE ##
            else:
                if time_delta > times_dict[time_good] + free_mean:
                    new_time_delta = times_dict[time_good] + free_mean
                else:
                    new_time_delta = time_delta
# ------------- break down adjustment per hour -------------  #
        else:
            new_time_delta = time_delta
        if entry["_links"]["replies"]["count"] > 0:
            #print len(tfr_list)
            tfr_list.append(new_time_delta)
            case_ids.append(entry["id"])


    try:
      next_page_url = BASE_API_URL + cases_json["_links"]["next"]["href"]
      cases = desk.get(next_page_url)

    except TypeError:
      break

  return tfr_list, case_ids, num_cases

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

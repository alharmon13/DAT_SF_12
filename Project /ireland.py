import datetime
import time
import json
import pprint
#import asana.stats.biz.uo.desk_common as desk
import desk_common as desk_util
from optparse import OptionParser

BASE_API_URL = "https://asana.desk.com"

def main(begin_episode, end_episode):
  begin_episode_ts = time.mktime(datetime.datetime.strptime(begin_episode, "%Y-%m-%d").timetuple())
  end_episode_ts = time.mktime(datetime.datetime.strptime(end_episode, "%Y-%m-%d").timetuple())

  channel = "email"
  status = "resolved,closed"
  per_page = 100
  desk = desk_util.connectToDesk()
  tfr_list = getCases(desk, begin_episode_ts, end_episode_ts, channel, status, per_page)
  avg_sum = sum(tfr_list, datetime.timedelta())
  avg_sum_h = (avg_sum.total_seconds())/3600
  list_len = len(tfr_list)
  print avg_sum, avg_sum_h, list_len
  average = float(avg_sum_h/list_len)
  print "Average =", average, ". Number of cases created during closed hours =", len(tfr_list)


def getCases(desk, since_created_at, max_created_at, channel, status, per_page):
  tfr_list = []
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
        too_long = datetime.timedelta(days=4)
        eight_hours = datetime.timedelta(hours=8)
        closed_hours = ["19", "20", "21", "22", "23", "0", "1", "2", "3", "4", "5", "6"]

        if entry["_links"]["assigned_group"] is not None:
        	if entry["_links"]["assigned_group"]["href"] not in specific_queues:
          		continue
        if entry["created_at"] is not None:
    		entryA = (datetime.datetime.strptime(entry["created_at"], '%Y-%m-%dT%H:%M:%SZ'))
    		entryB = (datetime.datetime.date(entryA))
    		entry_good_format = entryB.strftime('%Y-%m-%d')
    		if entry_good_format in excluded_dates:
    			continue
    		timeA = (datetime.datetime.time(entryA))
    		time_good = str(timeA.hour)
    		if time_good in closed_hours:
    			created_at_ts = datetime.datetime.strptime(entry["created_at"],"%Y-%m-%dT%H:%M:%SZ")
    		else:
    			continue
      	else:
        	continue
      	if entry["first_resolved_at"] is not None:
        	resolved_at_ts = datetime.datetime.strptime(entry["first_resolved_at"],"%Y-%m-%dT%H:%M:%SZ")
      	else:
        	continue
      	time_delta = resolved_at_ts - created_at_ts
      	if time_delta > too_long:
      		continue
        if time_delta > eight_hours:
            new_time_delta = time_delta - eight_hours
        else:
            new_time_delta = time_delta
      	if entry["_links"]["replies"]["count"] > 0:
        	tfr_list.append(new_time_delta)

    try:
      next_page_url = BASE_API_URL + cases_json["_links"]["next"]["href"]
      cases = desk.get(next_page_url)

    except TypeError:
      break
  return tfr_list


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

from libusac2.csv import parse_csv
from libusac2.util import RIDER_HEADERS, CLUB_HEADERS
from redis import Redis

import sys

if len(sys.argv) < 3:
    print("Usage: loader_redis.py <club-csv> <rider-csv> [<redis-port>]")
    exit(1)

club_file = sys.argv[1]
rider_file = sys.argv[2]
if len(sys.argv) == 4:
    redis_port = int(sys.argv[3])
else:
    redis_port = None

rds = Redis()

#rds.delete(*rds.keys('rider*'))
#rds.delete(*rds.keys('club*'))
#rds.delete(*rds.keys('team*'))

from datetime import datetime

print("Initializing load at %s" % datetime.now())

clubs = parse_csv(club_file, CLUB_HEADERS)
print(">> Clubs CSV parsed.")
riders = parse_csv(rider_file, RIDER_HEADERS)
print(">> Rider CSV parsed.")

for c in clubs:
    rds.hmset("club:%d" % int(c['club_id']), c)
    if c['team_id'] is not None:
        rds.hmset("team:%d" % int(c['team_id']), {'team_id': c['team_id'], 'team_name': str(c['team_name'])})

print(">> Clubs loaded.")

def get_if_not_none(val, cls):
    if val is None:
        return None
    else:
        return cls.query.get(val)

p = rds.pipeline()
x = 0
for r in riders:
    x += 1
    p.hmset("rider:%d" % int(r['license_number']), r)
    if x % 250 == 0:
        p.execute()
        p = rds.pipeline()

p.execute()
print(">> Riders loaded.")

rider_ct = len(rds.keys("rider*"))
team_ct = len(rds.keys("team*"))
club_ct = len(rds.keys("club*"))

print((">> Loaded %d clubs, %d teams, and %d members from CSV." % (club_ct, team_ct, rider_ct)))

print("Finished load at %s" % datetime.now())
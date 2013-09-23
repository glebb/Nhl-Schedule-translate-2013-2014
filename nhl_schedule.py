from BeautifulSoup import BeautifulSoup
import datetime
from dateutil import parser
import urllib2
import pytz
import cPickle as pickle

TARGET_TIMEZONE = pytz.timezone('Europe/Helsinki')
START_FROM = datetime.time(hour=7, minute=00)
END_BY = datetime.time(hour=22, minute=30)
FILTER = 'Philadelphia'
WRITE_ICAL_ENTRIES = True

if WRITE_ICAL_ENTRIES:
    import icalendar

try:
    games = pickle.load( open( "games.p", "rb" ) )
except IOError:
    data = urllib2.urlopen('http://www.nhl.com/ice/schedulebyseason.htm').read()
    soup = BeautifulSoup(data)

    table_cells = soup.findAll('td', {'class' : 'time'})
    games = []
    for td in table_cells:
        item = {}
        parent_row = td.findParents('tr')[0]
        game_info_cells = parent_row.findAll('td')
        item['date'] = str(game_info_cells[0].div.string)
        item['visiting_team'] = str(game_info_cells[1].findAll('a')[1].string)
        item['home_team'] = str(game_info_cells[2].findAll('a')[1].string)
        item['time'] = str(game_info_cells[3].div.string)
        games.append(item)
        pickle.dump( games, open( "games.p", "wb" ) )

i = 1
for game in games:
        date = game['date']
        visiting_team = game['visiting_team']
        home_team = game['home_team']
        time = game['time']
        
        if FILTER:
            if not home_team == FILTER and not visiting_team == FILTER:
                continue
        usa_et_time = parser.parse(date + ' ' + time).replace(tzinfo=pytz.timezone('US/Eastern'))
        target_time = usa_et_time.astimezone(TARGET_TIMEZONE)
    
        if target_time.time() >= START_FROM and target_time.time() <= END_BY:
            tagline = home_team + ' vs ' + visiting_team
            print str(i) + '. ' + target_time.strftime("%A %d.%m.%Y %H:%M") + ' ' + tagline
            i += 1
    
            if WRITE_ICAL_ENTRIES:
                cal = icalendar.Calendar()
                event = icalendar.Event()
                event.add('summary', 'NHL: ' + tagline)
                event.add('dtstart', target_time)
                event.add('dtend', target_time + datetime.timedelta(hours=2, minutes=30))
                cal.add_component(event)
                f = open(target_time.strftime("%Y-%m-%d - ") + tagline + '.ics', 'wb')
                f.write(cal.to_ical())
                f.close()

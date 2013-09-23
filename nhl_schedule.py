from BeautifulSoup import BeautifulSoup
import datetime
from dateutil import parser
import urllib2
import pytz
import cPickle as pickle

TARGET_TIMEZONE = pytz.timezone('Europe/Helsinki')
START_FROM = datetime.time(hour=7, minute=00)
END_BY = datetime.time(hour=22, minute=30)
TEAM_FILTER = 'Philadelphia'
WRITE_ICAL_ENTRIES = True
SCHEDULE_DATA = "games.p"

if WRITE_ICAL_ENTRIES:
    import icalendar

def main():
    try:
        games = pickle.load( open( SCHEDULE_DATA, "rb" ) )
    except IOError:
        games = _save_schedule_from_web()
    
    i = 1
    for game in games:
        date = game['date']
        visiting_team = game['visiting_team']
        home_team = game['home_team']
        time = game['time']
    
        if TEAM_FILTER:
            if not home_team == TEAM_FILTER and not visiting_team == TEAM_FILTER:
                continue
        usa_et_time = parser.parse(date + ' ' + time).replace(tzinfo=pytz.timezone('US/Eastern'))
        target_time = usa_et_time.astimezone(TARGET_TIMEZONE)

        if target_time.time() >= START_FROM and target_time.time() <= END_BY:
            tagline = home_team + ' vs ' + visiting_team
            print str(i) + '. ' + target_time.strftime("%A %d.%m.%Y %H:%M") + ' ' + tagline
            i += 1

            if WRITE_ICAL_ENTRIES:
                cal = _create_ical(tagline, target_time)
                f = open(target_time.strftime("%Y-%m-%d - ") + tagline + '.ics', 'wb')
                f.write(cal.to_ical())
                f.close()

def _save_schedule_from_web():
    games = []

    data = urllib2.urlopen('http://www.nhl.com/ice/schedulebyseason.htm').read()
    soup = BeautifulSoup(data)

    table_cells = soup.findAll('td', {'class' : 'time'})
    for td in table_cells:
        entry = _parse_game_entry_from(td)
        games.append(entry)
    pickle.dump( games, open( SCHEDULE_DATA, "wb" ) )
    return games
    
def _parse_game_entry_from(td):
    item = {}
    parent_row = td.findParents('tr')[0]
    game_info_cells = parent_row.findAll('td')
    item['date'] = str(game_info_cells[0].div.string)
    item['visiting_team'] = str(game_info_cells[1].findAll('a')[1].string)
    item['home_team'] = str(game_info_cells[2].findAll('a')[1].string)
    item['time'] = str(game_info_cells[3].div.string)
    return item

def _create_ical(tagline, target_time):
    cal = icalendar.Calendar()
    event = icalendar.Event()
    event.add('summary', 'NHL: ' + tagline)
    event.add('dtstart', target_time)
    event.add('dtend', target_time + datetime.timedelta(hours=2, minutes=30))
    cal.add_component(event)
    return cal
    
if __name__ == '__main__':
    main()
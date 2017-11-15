import os
import datetime
import time

from bs4 import BeautifulSoup

from scl_transport.gtfsdb.gtfsdb import FeedInfo, Database, Bus
from scl_transport.api.utils.positioning import PositioningFetcher
from .utils import LinkExtractor
from .tasks import send_email_async

BASE_URL = 'https://www.dtpm.cl/index.php/'
# @@TODO: save and use DB reference
REFERENCE_GTFS = '28-10-2017'


def analyze_available_gtfs():
    try:
        # get GTFS website link
        link_extractor = LinkExtractor(url=BASE_URL, contains_text="GTFS Vigente")
        # get GTFS website html
        link = link_extractor.link
        link_extractor = LinkExtractor(url=link)
        # get GTFS text
        soup = BeautifulSoup(link_extractor.response, 'html.parser')
        text_to_analize = soup.findAll('div', {'class': 'item-page'})[0].p.strong.text
        if REFERENCE_GTFS not in text_to_analize:
            msg = 'New available feed: {}'.format(text_to_analize)
            send_email_async(subject=msg, to_email=os.getenv('PROJECT_MAINTAINER'), content=msg)
        # save reference

        # get session
        kwargs = {}
        db = Database(**kwargs)
        # get feed
        feed_info = db.session.query(FeedInfo).first()
        feed_info.feed_download_url = link
        feed_info.feed_last_fetched_at = datetime.datetime.now()
        db.session.add(feed_info)
        db.session.commit()
    except Exception, e:
        msg = 'Error getting GTFS info: {}'.format(str(e))
        send_email_async(subject=msg, to_email=os.getenv('PROJECT_MAINTAINER'), content=msg)


def fetch_positioning_data():
    positioning_fetcher = PositioningFetcher(
        username=os.getenv('POSITIONING_WS_USERNAME'),
        password=os.getenv('POSITIONING_WS_PASSWORD')
    )
    kwargs = {}
    db = Database(**kwargs)

    api_results = positioning_fetcher.get_results()
    results = []
    for result in api_results:
        bus = Bus(
            bus_plate_number=result['bus_plate_number'],
            direction_id=result['direction_id'],
            bus_movement_orientation=result['bus_movement_orientation'],
            operator_number=result['operator_number'],
            bus_speed=result['bus_speed'],
            bus_lat=result['bus_lat'],
            bus_lon=result['bus_lon'],
            original_route_id=result['original_route_id'],
            console_route_id=result['console_route_id'],
            synoptic_route_id=result['synoptic_route_id'],
            captured_at=result['captured_at'],
            added_at=result['added_at'],
            geom=Bus.get_geom(result)
        )
        # safety checks
        if len(result['bus_plate_number']) < 4:
            continue
        if not result['direction_id']:
            continue
        if not result['original_route_id']:
            continue
        results.append(bus)

    start = time.time()
    # delete current records
    db.session.query(Bus).delete()
    db.session.commit()
    # insert new records
    print "inserting ...", len(results)
    db.session.bulk_save_objects(results)
    db.session.commit()
    end = time.time()
    print end - start

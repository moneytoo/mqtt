from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
from astral.geocoder import database, lookup
import pytz

class SunTimes:
    def __init__(self):
        self.city = lookup("Prague", database())
        self.timezone = pytz.timezone(self.city.timezone)
        self.offset_hours = timedelta(hours=1)
        self.sun_times = None
        self.sunrise = None
        self.sunset = None
        self.last_update_date = None
        self.__update_sun_times()

    def __update_sun_times(self):
        print(self.city)
        now = datetime.now(self.timezone)
        current_date = now.date()
        if self.last_update_date != current_date:
            self.sun_times = sun(self.city.observer, date=now, tzinfo=self.city.timezone)
            self.sunrise = self.sun_times["sunrise"] + self.offset_hours
            self.sunset = self.sun_times["sunset"] - self.offset_hours
            self.last_update_date = current_date

    def is_day(self):
        self.__update_sun_times()
        now = datetime.now(self.timezone)
        return self.sunrise < now < self.sunset

    def is_night(self):
        return not self.is_day()

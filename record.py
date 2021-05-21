import csv
from _datetime import timedelta


class Record:
    def __init__(self, **whatever):
        self.__dict__.update(whatever)

    def write_to_csv(self, file_handle):
        writer = csv.DictWriter(file_handle, self.__dict__.keys())
        writer.writerow(self.__dict__)


class FoundRecord(Record):
    def __init__(self, username, location, date):
        super().__init__(username=username, location=location, date=date)


class NotFoundRecord(Record):
    def __init__(self, username, location, date):
        super().__init__(
            username=username,
            location=location,
            start_date=date,
            end_date=(date + timedelta(days=15)),
        )

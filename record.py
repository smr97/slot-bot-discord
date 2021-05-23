import csv
import os
import re
import asyncio
from _datetime import timedelta
import datetime


class LocationError(Exception):
    def __init__(self, base_exception, **whatever):
        super().__init__(whatever)
        self.base_exception = base_exception


class DateError(Exception):
    def __init__(self, base_exception, **whatever):
        super().__init__(whatever)
        self.base_exception = base_exception


class StatError(Exception):
    def __init__(self, **whatever):
        super().__init__(whatever)


class Record:
    def __init__(self, **whatever):
        self.__dict__.update(whatever)

    def write_to_csv(self, file_handle):
        writer = csv.DictWriter(file_handle, self.__dict__.keys())
        writer.writerow(self.__dict__)


class FoundRecord(Record):
    def __init__(self, username, location, date):
        super().__init__(username=username, location=location, date=date)

    def __str__(self):
        return (
            f"{self.username} found an interview slot at {self.location} on {self.date}"
        )


class NotFoundRecord(Record):
    def __init__(self, username, location, date):
        super().__init__(
            username=username,
            location=location,
            start_date=date,
            end_date=(date + timedelta(days=15)),
        )


class MessageStore:
    def __init__(self, maxsize):
        self.locations = ["mumbai", "delhi", "kolkata", "hyderabad", "chennai"]
        self.found_queue = asyncio.Queue(maxsize=maxsize)
        self.not_found_queue = asyncio.Queue(maxsize=maxsize)

    def parse_message(self, found_string):
        try:
            loc = next(_l for _l in self.locations if _l in found_string)
        except Exception as e:
            raise LocationError(e)
        try:
            match = re.search(r"(\d+/\d+/\d+)", found_string).group(1)
            date = datetime.datetime.strptime(match, "%d/%m/%y")
        except Exception as e:
            raise DateError(e)
        return loc, date

    def enqueue_message(self, message_str, username):
        if "got" in message_str or "found" in message_str:
            status = True
        elif "tried" in message_str:
            status = False
        else:
            raise StatError()
        loc, date = self.parse_message(message_str)
        if status:
            try:
                self.found_queue.put_nowait(FoundRecord(username, loc, date))
            except asyncio.QueueFull:
                self._flush_found_queue()

        else:
            try:
                self.not_found_queue.put_nowait(NotFoundRecord(username, loc, date))
            except asyncio.QueueFull:
                self._flush_not_found_queue()

        return status

    def flush_queues(self):
        self._flush_found_queue()
        self._flush_not_found_queue()

    def _flush_found_queue(self):
        today = datetime.date.today().strftime("%d_%m_%y")
        with open(f"SlotsFound_{today}.csv", "a") as csvhandle:
            while True:
                try:
                    rec = self.found_queue.get_nowait()
                    rec.write_to_csv(csvhandle)
                except asyncio.QueueEmpty:
                    break

    def _flush_not_found_queue(self):
        today = datetime.date.today().strftime("%d_%m_%y")
        with open(f"SlotsNotFound_{today}.csv", "a") as csvhandle:
            while True:
                try:
                    rec = self.not_found_queue.get_nowait()
                    rec.write_to_csv(csvhandle)
                except asyncio.QueueEmpty:
                    break

    def query_slots(self):
        if not self.found_queue.empty():
            records = [_s for _s in self.found_queue._queue]
        else:
            today = datetime.date.today().strftime("%d_%m_%y")
            with open(f"SlotsFound_{today}.csv", "r") as csvhandle:
                rows = csv.reader(csvhandle)
                records = [FoundRecord(_r[0], _r[1], _r[2]) for _r in rows]
        return records

    def get_all_files(self):
        all_files = [open(_f, "rb") for _f in os.listdir(".") if "SlotsFound" in _f]
        return all_files



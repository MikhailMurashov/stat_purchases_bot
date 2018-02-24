import logging
import time

from helper_classes.cashvoucher import CashVoucher
from helper_classes.date import Date

logger = logging.getLogger(__name__)


class User:
    def __init__(self, _id):
        self.id = _id
        self.total_sum = 0
        self.archive = {}

    def clear_archive(self):
        self.archive.clear()
        self.total_sum = 0

    def add_purchase(self, file_path):
        cash_voucher = CashVoucher()
        cash_voucher.load_from_file(file_path)

        self.total_sum += cash_voucher.total_sum

        date = cash_voucher.date_time
        date_key = date.get_date_key()

        if not (date_key in self.archive):
            self.archive[date_key] = []
        self.archive[date_key].append(cash_voucher)

    def get_day_sum(self, date):
        result_sum = 0
        date_key = date.get_date_key()
        if date_key in self.archive:
            cash_vouchers = self.archive[date_key]
            for cash_voucher in cash_vouchers:
                result_sum += cash_voucher.total_sum

        return result_sum

    def get_today_sum(self):
        unix_today = time.time()
        date = Date()
        date.from_unix_format(unix_today)

        return self.get_day_sum(date)

    def get_month_sum(self):
        result_sum = 0
        unix_today = time.time()
        date = Date()
        date.from_unix_format(unix_today)

        while int(date.day) > 1:
            result_sum += self.get_day_sum(date)
            date.subtract_day()

        first_day_sum = self.get_day_sum(date)
        result_sum += first_day_sum

        return result_sum

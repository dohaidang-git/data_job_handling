"""Unit tests cho các hàm xử lý dữ liệu tuyển dụng."""
import math
import unittest

import numpy as np

from processing.data_processing import (
    address_separate,
    classify_job_title,
    salary_to_numeric,
)


class SalaryTests(unittest.TestCase):
    def test_range_in_millions(self):
        self.assertEqual(salary_to_numeric('10 - 20 triệu'), (10_000_000, 20_000_000, 'VND'))

    def test_up_to(self):
        minimum, maximum, unit = salary_to_numeric('Tới 35 triệu')
        self.assertTrue(math.isnan(minimum))
        self.assertEqual((maximum, unit), (35_000_000, 'VND'))

    def test_above(self):
        minimum, maximum, unit = salary_to_numeric('Trên 3 triệu')
        self.assertEqual((minimum, unit), (3_000_000, 'VND'))
        self.assertTrue(math.isnan(maximum))

    def test_usd_range(self):
        self.assertEqual(salary_to_numeric('600 - 1,300 USD'), (600, 1300, 'USD'))

    def test_missing_or_negotiable(self):
        for value in (np.nan, 'Thỏa thuận', 'Thoả thuận'):
            with self.subTest(value=value):
                self.assertTrue(all(isinstance(x, float) and math.isnan(x) for x in salary_to_numeric(value)))

    def test_from_million_is_minimum(self):
        minimum, maximum, unit = salary_to_numeric('Từ 18 triệu')
        self.assertEqual((minimum, unit), (18_000_000, 'VND'))
        self.assertTrue(math.isnan(maximum))

    def test_decimal_million_range(self):
        self.assertEqual(salary_to_numeric('6.8 - 10 triệu'), (6_800_000, 10_000_000, 'VND'))


class AddressTests(unittest.TestCase):
    def test_multiple_cities_and_districts(self):
        self.assertEqual(address_separate('Hà Nội: Ba Đình, Cầu Giấy: Hồ Chí Minh: Quận 7'), {
            'city1': 'Hà Nội', 'district1_1': 'Ba Đình', 'district1_2': 'Cầu Giấy',
            'city2': 'Hồ Chí Minh', 'district2_1': 'Quận 7',
        })

    def test_missing_address(self):
        self.assertEqual(address_separate(np.nan), {})

    def test_new_location_label(self):
        self.assertEqual(address_separate('Hồ Chí Minh (mới)'), {'city1': 'Hồ Chí Minh'})


class ClassificationTests(unittest.TestCase):
    def test_common_titles(self):
        examples = {
            'Java Developer': 'Software Development',
            'Manual Tester': 'Testing',
            'Data Engineer': 'Data & AI',
            'Kỹ Sư Cầu Nối (Brse)': 'Business Development/BI/BA',
            'IT Comtor': 'Project & Product Management',
        }
        for title, expected in examples.items():
            with self.subTest(title=title):
                self.assertEqual(classify_job_title(title), expected)

    def test_missing_title(self):
        self.assertEqual(classify_job_title(np.nan), 'Other')


if __name__ == '__main__':
    unittest.main()

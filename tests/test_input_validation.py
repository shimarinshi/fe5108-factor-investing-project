import csv
import tempfile
import unittest
from pathlib import Path
from src.input_validation import COLUMNS, inspect_csv

class InputValidationTests(unittest.TestCase):
    def inspect(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            with path.open('w', newline='') as stream:
                writer = csv.writer(stream); writer.writerow(COLUMNS); writer.writerows(rows)
            return inspect_csv(path)

    def test_raw_outlier_is_preserved_and_missing_is_counted(self):
        result = self.inspect([['001', '12/31/1998', '.5', '.2', '30.176', '', '.8']])
        self.assertEqual(result['ranges']['R1M_Usd'], [30.176, 30.176])
        self.assertEqual(result['missing_by_field']['Vol3Y_Usd'], 1)
        self.assertEqual(result['formation_start'], '1998-12-31')

    def test_duplicate_key_fails(self):
        row = ['1', '12/31/1998', '.5', '.2', '.1', '.3', '.8']
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.inspect([row, row])

    def test_non_month_end_fails(self):
        with self.assertRaisesRegex(ValueError, 'month end'):
            self.inspect([['1', '12/30/1998', '.5', '.2', '.1', '.3', '.8']])

"""Kiểm thử import; PostgreSQL integration test chỉ chạy khi được bật."""
import os
import unittest
import uuid
from unittest.mock import MagicMock, patch

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from processing.import_to_sql import import_jobs, make_csv_key, make_topcv_key, main


class JobKeyTests(unittest.TestCase):
    def test_csv_key_ignores_query_parameters(self):
        self.assertEqual(make_csv_key('https://example.com/job/1?tracking=abc'),
                         make_csv_key('https://example.com/job/1?tracking=xyz'))

    def test_csv_key_changes_for_different_links(self):
        self.assertNotEqual(make_csv_key('https://example.com/job/1'),
                            make_csv_key('https://example.com/job/2'))

    def test_missing_csv_link(self):
        for value in (None, '', float('nan')):
            with self.subTest(value=value):
                self.assertIsNone(make_csv_key(value))

    def test_topcv_url_formats(self):
        for link in ('https://www.topcv.vn/viec-lam/a/123.html',
                     'https://www.topcv.vn/brand/a/tuyen-dung/a-j123.html?track=1'):
            with self.subTest(link=link):
                self.assertEqual(make_topcv_key(link), 'topcv_123')

    def test_invalid_topcv_url(self):
        self.assertIsNone(make_topcv_key('https://www.topcv.vn/'))


class ImportUnitTests(unittest.TestCase):
    @patch('processing.import_to_sql.create_engine')
    @patch('processing.import_to_sql.pd.read_csv', side_effect=OSError('cannot read CSV'))
    @patch.dict(os.environ, {'DB_USER': 'test', 'DB_PASSWORD': 'test', 'DB_HOST': 'localhost', 'DB_NAME': 'test'})
    def test_engine_disposed_when_read_fails(self, read_csv, create_engine_mock):
        engine = create_engine_mock.return_value
        with self.assertRaises(OSError):
            main()
        engine.dispose.assert_called_once()

    def test_import_passes_conflict_handler(self):
        frame = pd.DataFrame([{'job_key': 'topcv_123', 'job_title': 'Developer'}])
        engine = MagicMock()
        with patch.object(pd.DataFrame, 'to_sql', autospec=True) as to_sql:
            import_jobs(frame, engine, table_name='jobs_test')
        self.assertEqual(to_sql.call_args.kwargs['name'], 'jobs_test')
        self.assertTrue(callable(to_sql.call_args.kwargs['method']))
        self.assertEqual(to_sql.call_args.kwargs['if_exists'], 'append')


@unittest.skipUnless(os.environ.get('RUN_POSTGRES_TESTS') == '1',
                     'Set RUN_POSTGRES_TESTS=1 to run PostgreSQL integration tests')
class PostgresIntegrationTests(unittest.TestCase):
    def test_duplicate_import_is_ignored(self):
        url = URL.create('postgresql+psycopg2', username=os.environ['DB_USER'],
                         password=os.environ['DB_PASSWORD'], host=os.environ['DB_HOST'],
                         port=int(os.environ.get('DB_PORT', '5432')),
                         database=os.environ['DB_NAME'])
        engine = create_engine(url)
        table_name = 'test_jobs_' + uuid.uuid4().hex
        try:
            with engine.begin() as connection:
                connection.execute(text(f'CREATE TEMPORARY TABLE "{table_name}" (job_key TEXT PRIMARY KEY, job_title TEXT) ON COMMIT DROP'))
                frame = pd.DataFrame([{'job_key': 'topcv_123', 'job_title': 'Developer'}])
                import_jobs(frame, connection, table_name=table_name)
                import_jobs(frame, connection, table_name=table_name)
                count = connection.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar_one()
                self.assertEqual(count, 1)
        finally:
            engine.dispose()


if __name__ == '__main__':
    unittest.main()

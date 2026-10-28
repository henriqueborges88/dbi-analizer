"""Dashboard regressions using SQLite in memory; never start VirtualBox or the agent."""
import importlib.util
import io
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import zipfile

from flask import template_rendered

SERVER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER))

import models
import utils
import virtualbox_manager


def load_test_app():
    original_init = models.db.init_app

    def initialize_in_memory(app):
        app.config.update(SQLALCHEMY_DATABASE_URI='sqlite://', TESTING=True)
        original_init(app)

    spec = importlib.util.spec_from_file_location('dashboard_test_app', SERVER / 'app.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    with patch.object(models.db, 'init_app', side_effect=initialize_in_memory), \
            patch.object(utils, 'write_ip_to_file') as write_ip, \
            patch.object(virtualbox_manager, 'configure_hostonly_network') as configure_network, \
            patch('threading.Thread.start') as start_thread:
        spec.loader.exec_module(module)
        write_ip.assert_called_once()
        configure_network.assert_called_once()
        start_thread.assert_called_once()
    return module.app


APP = load_test_app()


@contextmanager
def captured_context():
    contexts = []

    def record(sender, template, context, **extra):
        contexts.append(context)

    template_rendered.connect(record, APP)
    try:
        yield contexts
    finally:
        template_rendered.disconnect(record, APP)


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.hrefs = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.hrefs.extend(value for name, value in attrs if name == 'href')


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.context = APP.app_context()
        self.context.push()
        models.db.drop_all()
        models.db.create_all()
        self.client = APP.test_client()

    def tearDown(self):
        models.db.session.remove()
        models.db.drop_all()
        self.context.pop()

    def seed(self):
        models.db.session.add_all([
            models.Sample(hash_sha256='a' * 64, pin_tool_success=True,
                          dynamorio_tool_success=False, frida_tool_success=True),
            models.Sample(hash_sha256='b' * 64, pin_tool_success=False,
                          dynamorio_tool_success=True, frida_tool_success=False),
        ])
        models.db.session.commit()

    def filtered_hashes(self, tool, field, rule):
        with captured_context() as contexts:
            response = self.client.get('/sample/list', query_string={
                'tool_name': tool, 'field': field, 'rule': rule,
            })
        self.assertEqual(response.status_code, 200)
        return [sample.hash_sha256 for sample in contexts[-1]['samples']]

    def test_empty_pages_render(self):
        for path in ['/sample/list', '/sample/tools', '/analysis', '/upload', '/register']:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'dbi-analyzer', response.data)
                self.assertNotIn(b'cdn.jsdelivr', response.data)
        self.assertIn('Nenhuma amostra', self.client.get('/sample/list').text)

    def test_instrumentation_filters(self):
        self.seed()
        for tool, success in [('pin', 'a'), ('dynamorio', 'b'), ('frida', 'a')]:
            with self.subTest(tool=tool):
                failure = 'b' if success == 'a' else 'a'
                self.assertEqual(self.filtered_hashes(tool, 'result', 'success'), [success * 64])
                self.assertEqual(self.filtered_hashes(tool, 'result', 'fail'), [failure * 64])

    def test_unknown_and_incomplete_filters_are_not_treated_as_failures(self):
        self.seed()
        for query in [
            {'tool_name': 'pin', 'field': 'result', 'rule': 'typo'},
            {'tool_name': 'pin', 'field': 'name', 'rule': 'fail'},
            {'tool_name': 'unknown', 'field': 'name', 'rule': 'x'},
            {'tool_name': 'die'},
            {'rule': 'x'},
        ]:
            with self.subTest(query=query):
                self.assertEqual(self.client.get('/sample/list', query_string=query).status_code, 404)

    def test_missing_instrumentation_flags_match_the_failure_summary(self):
        self.seed()
        models.db.session.execute(models.db.update(models.Sample).values(pin_tool_success=None))
        models.db.session.commit()
        self.assertEqual(self.filtered_hashes('pin', 'result', 'fail'), ['a' * 64, 'b' * 64])
        self.assertEqual(self.filtered_hashes('pin', 'result', 'success'), [])

    def test_valid_filter_with_no_matches_is_an_empty_page(self):
        self.seed()
        self.assertEqual(self.filtered_hashes('die', 'name', 'not present'), [])

    def test_special_characters_round_trip_through_links(self):
        self.seed()
        label = '/literal %2F / & # São "<script>"'
        models.db.session.add(models.DieInfo(sample_hash_sha256='a' * 64, name=label, type='Packer'))
        models.db.session.commit()
        html = self.client.get('/sample/tools').text
        links = Links(html).hrefs
        matching = [link for link in links if parse_qs(urlsplit(link).query).get('rule') == [label]]
        self.assertTrue(matching)
        self.assertNotIn('<script>"</a>', html)
        with captured_context() as contexts:
            response = self.client.get(matching[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual([sample.hash_sha256 for sample in contexts[-1]['samples']], ['a' * 64])

    def test_detection_filters_and_distinct_samples(self):
        self.seed()
        for model, field, tool in [
            (models.DieInfo, 'name', 'die'), (models.DieInfo, 'type', 'die'),
            (models.YaraInfo, 'rule', 'yara'), (models.YaraInfo, 'namespace', 'yara'),
            (models.CapaInfo, 'name', 'capa'), (models.CapaInfo, 'namespace', 'capa'),
        ]:
            with self.subTest(tool=tool, field=field):
                rows = [model(sample_hash_sha256='a' * 64, **{field: 'match'}) for _ in range(2)]
                models.db.session.add_all(rows)
                models.db.session.commit()
                self.assertEqual(self.filtered_hashes(tool, field, 'match'), ['a' * 64])

    def test_frequencies_distinguish_occurrences_from_samples_and_drive_charts(self):
        self.seed()
        models.db.session.add_all([
            models.DieInfo(sample_hash_sha256='a' * 64, name='test', type='Packer'),
            models.DieInfo(sample_hash_sha256='a' * 64, name='test', type='Packer'),
            models.DieInfo(sample_hash_sha256='b' * 64, name='test', type='Packer'),
        ])
        models.db.session.commit()
        with captured_context() as contexts:
            response = self.client.get('/sample/tools')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(contexts[-1]['die_type']['Packer'], {
            'die_type_sample_freq': 2, 'die_type_freq': 3,
        })
        self.assertIn('max="3" value="3"', response.text)
        self.assertNotIn('createChart', response.text)

    def test_capa_name_keeps_all_namespaces(self):
        self.seed()
        models.db.session.add_all([
            models.CapaInfo(sample_hash_sha256='a' * 64, name='shared', namespace='one'),
            models.CapaInfo(sample_hash_sha256='b' * 64, name='shared', namespace='two'),
        ])
        models.db.session.commit()
        with captured_context() as contexts:
            response = self.client.get('/sample/tools')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(contexts[-1]['capa_name_categories']['shared'], {'one', 'two'})

    def test_details_handle_missing_fields_and_use_plural_capa_references(self):
        self.seed()
        models.db.session.add_all([
            models.DieInfo(sample_hash_sha256='a' * 64),
            models.YaraInfo(sample_hash_sha256='a' * 64, reference='javascript:alert(1)'),
            models.CapaInfo(sample_hash_sha256='a' * 64, references='https://example.test/reference'),
        ])
        models.db.session.commit()
        response = self.client.get('/sample/details/' + 'a' * 64)
        self.assertEqual(response.status_code, 200)
        self.assertIn('https://example.test/reference', response.text)
        self.assertNotIn('href="javascript:', response.text)
        self.assertIn('data-bs-toggle="tab"', response.text)
        self.assertNotIn('data-toggle="tab"', response.text)

    def test_unknown_sample_returns_not_found(self):
        self.assertEqual(self.client.get('/sample/details/' + 'f' * 64).status_code, 404)

    def test_register_rejects_invalid_hashes(self):
        for value in ['', '../outside', '<script>alert(1)</script>', 'g' * 64, 'a' * 63]:
            with self.subTest(value=value):
                self.assertEqual(self.client.post('/register', data={'hash_sha256': value}).status_code, 400)
        self.assertEqual(models.Sample.query.count(), 0)

    def test_register_normalizes_hash_and_returns_json(self):
        response = self.client.post('/register', data={'hash_sha256': 'A' * 64})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['hash_sha256'], 'a' * 64)
        self.assertEqual(response.mimetype, 'application/json')

    def test_upload_ignores_client_filename_and_stays_in_results_directory(self):
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as output:
            output.writestr('harmless.txt', 'fixture')
        expected_bytes = archive.getvalue()
        archive.seek(0)
        module = sys.modules[APP.import_name]
        with TemporaryDirectory(prefix='dbi-upload-test-') as directory, \
                patch.dict(APP.config, {'RESULTS_DIRECTORY': directory}), \
                patch.object(module, 'process_result') as process:
            response = self.client.post('/upload', data={
                'hash_sha256': 'A' * 64,
                'file': (archive, '../../outside.zip'),
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['filename'], 'a' * 64 + '.zip')
            files = list(Path(directory).iterdir())
            self.assertEqual([file.name for file in files], ['a' * 64 + '.zip'])
            self.assertEqual(files[0].read_bytes(), expected_bytes)
            process.assert_called_once_with(str(files[0]))

    def test_upload_rejects_invalid_hashes_and_non_zip_files_without_processing(self):
        module = sys.modules[APP.import_name]
        with TemporaryDirectory(prefix='dbi-upload-test-') as directory, \
                patch.dict(APP.config, {'RESULTS_DIRECTORY': directory}), \
                patch.object(module, 'process_result') as process:
            for value in ['../outside', 'a' * 64]:
                response = self.client.post('/upload', data={
                    'hash_sha256': value, 'file': (io.BytesIO(b'not a ZIP'), 'file.zip'),
                })
                self.assertEqual(response.status_code, 400)
            self.assertEqual(list(Path(directory).iterdir()), [])
            process.assert_not_called()


if __name__ == '__main__':
    unittest.main()

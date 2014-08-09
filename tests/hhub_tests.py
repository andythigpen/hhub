import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hhub'))

import unittest
from unittest import mock
import hhub
import json
from io import StringIO

class ConfigTestCase(unittest.TestCase):
    @mock.patch('hhub.os')
    def test_load(self, mock_os):
        m = mock.mock_open(read_data='{"ip":"1.2.3.4", "username":"abc"}')
        with mock.patch('hhub.open', m, create=True):
            cfg = hhub.Config('~/.hhub/config.json')
        self.assertEqual(cfg['ip'], '1.2.3.4')
        self.assertEqual(cfg['username'], 'abc')

    @mock.patch('hhub.os')
    def test_file_does_not_exist(self, mock_os):
        mock_os.configure_mock(**{'path.exists.return_value':False})
        m = mock.mock_open()
        with self.assertRaises(Exception) as cm:
            with mock.patch('hhub.open', m, create=True):
                cfg = hhub.Config('~/.hhub/config.json')

    @unittest.skip('Does not work since we cannot guarantee write is only called once.')
    @mock.patch('hhub.os')
    def test_save(self, mock_os):
        s = StringIO()
        mm = mock.MagicMock(return_value=s)
        m = mock.mock_open(mm, read_data='')
        m.configure_mock(**{'wraps':s})
        with mock.patch('hhub.open', m, create=True):
            cfg = hhub.Config('~/.hhub/config.json')
            cfg['ip'] = '4.3.2.1'
            cfg.save()
        handle = m()
        #FIXME: figure out a way to get the entire contents from mock object
        handle.write.assert_called_once_with('{"ip": "4.3.2.1"}')

class NotificationTestCase(unittest.TestCase):
    def test_notify(self):
        ch = hhub.NotificationChannel()
        m = mock.Mock()
        ch.register('test', m)
        ch.notify('test', one=1)
        m.on_event.assert_called_once_with(one=1)

    def test_notify_another(self):
        ch = hhub.NotificationChannel()
        m = mock.Mock()
        ch.register('one', m)
        ch.notify('two', data=2)
        self.assertFalse(m.called)

if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

import unittest
from unittest import mock

from mantidimaging.core.utility.version_check import (CheckVersion, _version_is_uptodate, _make_version_str,
                                                      _parse_version)


class TestCheckVersion(unittest.TestCase):
    def setUp(self):
        with mock.patch("mantidimaging.core.utility.version_check.CheckVersion._retrieve_versions"):
            self.versions = CheckVersion()
            self.versions._use_test_values()

    def test_parse_version(self):
        parsed = _parse_version("9.9.9_1234")

        assert parsed.version == (9, 9, 9)
        assert parsed.commits == 1234

    def test_make_version_str(self):
        input_version_str = "9.9.9_1234"
        parsed = _parse_version(input_version_str)

        version_string = _make_version_str(parsed)

        assert version_string == input_version_str

    def test_version_is_uptodate(self):
        for local, remote, is_uptodate in [
            ["8.9.9_1234", "9.9.9_1234", False],
            ["9.9.9_1234", "19.9.9_1234", False],
            ["9.9.9_1234", "19.9.9_0", False],
            ["9.9.9_1", "9.9.9_2", False],
            ["8.9.9_1234", "8.9.9_1234", True],
            ["9.9.9_1234", "8.9.9_1234", True],
            ["8.9.9_2000", "8.9.9_1234", True],
            ["8.10.9_1234", "8.9.9_1234", True],
        ]:

            local_parsed = _parse_version(local)
            remote_parsed = _parse_version(remote)

            self.assertEqual(_version_is_uptodate(local_parsed, remote_parsed), is_uptodate)

    def test_is_conda_uptodate(self):
        self.assertTrue(self.versions.is_conda_uptodate())

        self.versions._use_test_values(False)
        self.assertFalse(self.versions.is_conda_uptodate())

    def test_conda_update_message(self):
        self.versions._use_test_values(False)
        msg, detailed = self.versions.conda_update_message()
        self.assertTrue("Found version 1.0.0_1" in msg)
        self.assertTrue("latest: 2.0.0_1" in msg)
        self.assertTrue("To update your environment" in detailed)

    @mock.patch("builtins.print")
    def test_show_versions(self, mock_print):
        self.versions.show_versions()
        mock_print.assert_called()

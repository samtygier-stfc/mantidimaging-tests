from __future__ import absolute_import, division, print_function

import unittest

import numpy.testing as npt

from mantidimaging import helper as h
from mantidimaging.core.filters import rebin
from mantidimaging.tests import test_helper as th


class RebinTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RebinTest, self).__init__(*args, **kwargs)

    def test_not_executed_rebin_none(self):
        images, control = th.gen_img_shared_array_and_copy()
        val = None
        mode = 'nearest'
        result = rebin.execute(images, val, mode)
        npt.assert_equal(result, control)

    def test_not_executed_rebin_negative(self):
        images, control = th.gen_img_shared_array_and_copy()
        mode = 'nearest'
        val = -1
        result = rebin.execute(images, val, mode)
        npt.assert_equal(result, control)

    def test_not_executed_rebin_zero(self):
        images, control = th.gen_img_shared_array_and_copy()
        mode = 'nearest'
        val = 0
        result = rebin.execute(images, val, mode)
        npt.assert_equal(result, control)

    def test_executed_par_2(self):
        self.do_execute(2.)

    def test_executed_par_5(self):
        self.do_execute(5.)

    def test_executed_seq_2(self):
        th.switch_mp_off()
        self.do_execute(2.)
        th.switch_mp_on()

    def test_executed_seq_5(self):
        th.switch_mp_off()
        self.do_execute(5.)
        th.switch_mp_on()

    def do_execute(self, val=2.):
        images = th.gen_img_shared_array()
        mode = 'nearest'

        expected_x = int(images.shape[1] * val)
        expected_y = int(images.shape[2] * val)
        result = rebin.execute(images, val, mode)
        npt.assert_equal(result.shape[1], expected_x)
        npt.assert_equal(result.shape[2], expected_y)

    def test_memory_change_acceptable(self):
        """
        This filter will increase the memory usage
        as it has to allocate memory for the new resized shape
        """
        images = th.gen_img_shared_array()
        mode = 'nearest'
        # This about doubles the memory. Value found from running the test
        val = 100.
        expected_x = int(images.shape[1] * val)
        expected_y = int(images.shape[2] * val)
        cached_memory = h.get_memory_usage_linux(kb=True)[0]
        result = rebin.execute(images, val, mode)
        self.assertLess(
            h.get_memory_usage_linux(kb=True)[0], cached_memory * 2)
        npt.assert_equal(result.shape[1], expected_x)
        npt.assert_equal(result.shape[2], expected_y)


if __name__ == '__main__':
    unittest.main()
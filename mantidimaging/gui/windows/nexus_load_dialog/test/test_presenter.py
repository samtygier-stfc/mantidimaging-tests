# Copyright (C) 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

import unittest
from unittest import mock

import h5py
import numpy as np

from mantidimaging.core.data.dataset import Dataset
from mantidimaging.gui.windows.nexus_load_dialog.presenter import _missing_data_message, TOMO_ENTRY, DATA_PATH, \
    IMAGE_KEY_PATH, NexusLoadPresenter
from mantidimaging.gui.windows.nexus_load_dialog.presenter import logger as nexus_logger
from mantidimaging.gui.windows.nexus_load_dialog.view import NexusLoadDialog


def test_missing_field_message():
    assert _missing_data_message("missing_data") == "The NeXus file does not contain the required missing_data data."


class NexusLoaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.nexus = h5py.File("data", "w", driver="core", backing_store=False)
        self.full_tomo_path = f"entry1/{TOMO_ENTRY}"
        self.tomo_entry = self.nexus.create_group(self.full_tomo_path)

        self.n_images = 10
        self.data_array = np.random.random((self.n_images, 10, 10))
        self.tomo_entry.create_dataset(DATA_PATH, data=self.data_array, dtype="float64")

        self.flat_before = self.data_array[:2]
        self.dark_before = self.data_array[2:4]
        self.sample = self.data_array[4:6]
        self.dark_after = self.data_array[6:8]
        self.flat_after = self.data_array[8:]

        self.image_key_array = np.array([1, 1, 2, 2, 0, 0, 2, 2, 1, 1])
        self.tomo_entry.create_dataset(IMAGE_KEY_PATH, data=self.image_key_array)
        self.title = "my_data_title"
        self.tomo_entry.create_dataset("title", shape=(1, ), data=self.title.encode("UTF-8"))

        self.view = mock.Mock(autospec=NexusLoadDialog)
        self.view.filePathLineEdit.text.return_value = "filename"
        self.view.pixelDepthComboBox.currentText.return_value = self.expected_pixel_depth = "float32"
        self.view.pixelSizeSpinBox.value.return_value = pixel_size = 9.00
        self.expected_pixel_size = int(pixel_size)

        self.image_types = ["Projections", "Flat Before", "Flat After", "Dark Before", "Dark After"]
        self.view.checkboxes = dict()

        for image_type in self.image_types:
            checkbox_mock = mock.Mock()
            checkbox_mock.isChecked.return_value = True
            self.view.checkboxes[image_type] = checkbox_mock

        self.nexus_loader = NexusLoadPresenter(self.view)
        self.nexus_loader.nexus_file = self.nexus

        self.nexus_load_patcher = mock.patch("mantidimaging.gui.windows.nexus_load_dialog.presenter.h5py.File")
        self.nexus_load_mock = self.nexus_load_patcher.start()
        self.nexus_load_mock.return_value = self.nexus

    def tearDown(self) -> None:
        self.nexus.close()
        self.nexus_load_patcher.stop()

    def replace_values_in_image_key(self, name: str, new_value: int):
        """
        Changes values in the image key.
        :param name: The name of the image type.
        :param new_value: The new image key value.
        """
        before = "Before" in name
        if "Flat" in name:
            prev_value = 1
        elif "Dark" in name:
            prev_value = 2
        else:
            prev_value = 0

        if before or prev_value == 0:
            self.tomo_entry[IMAGE_KEY_PATH][:self.n_images // 2] = np.where(
                self.tomo_entry[IMAGE_KEY_PATH][:self.n_images // 2] == prev_value, new_value,
                self.tomo_entry[IMAGE_KEY_PATH][:self.n_images // 2])
        if not before:
            self.tomo_entry[IMAGE_KEY_PATH][self.n_images // 2:] = np.where(
                self.tomo_entry[IMAGE_KEY_PATH][self.n_images // 2:] == prev_value, new_value,
                self.tomo_entry[IMAGE_KEY_PATH][self.n_images // 2:])

    def test_look_for_nx_tomo_entry_successful(self):
        self.assertIsNotNone(self.nexus_loader._look_for_nxtomo_entry())

    def test_look_for_nx_tomo_entry_unsuccessful(self):
        required_data_paths = [
            self.full_tomo_path, self.full_tomo_path + "/" + DATA_PATH, self.full_tomo_path + "/" + IMAGE_KEY_PATH
        ]
        error_names = [TOMO_ENTRY, DATA_PATH, IMAGE_KEY_PATH]
        self.tearDown()  # Close the existing NeXus file
        for i in range(len(required_data_paths)):
            self.setUp()
            del self.nexus[required_data_paths[i]]
            with self.subTest(i=i):
                missing_string = _missing_data_message(error_names[i])
                with self.assertLogs(nexus_logger, level="ERROR") as log_mock:
                    self.nexus_loader.scan_nexus_file()
                    self.assertIn(missing_string, log_mock.output[0])
                self.view.show_missing_data_error.assert_called_once_with(missing_string)
                self.view.disable_ok_button.assert_called_once()
            self.tearDown()

    def test_no_data_or_image_key_not_found_indicated_on_view(self):
        paths = [IMAGE_KEY_PATH, DATA_PATH]
        positions = [0, 1]
        self.tearDown()
        for i in range(len(paths)):
            self.setUp()
            del self.tomo_entry[paths[i]]
            with self.subTest(i=i):
                self.nexus_loader.scan_nexus_file()
                self.view.set_data_found.assert_called_with(positions[i], False, "", ())
            self.tearDown()

    def test_data_and_image_key_found_indicated_on_view(self):
        self.nexus_loader.scan_nexus_file()
        self.view.set_data_found.assert_any_call(0, True, f"{self.full_tomo_path}/{IMAGE_KEY_PATH}",
                                                 self.image_key_array.shape)
        self.view.set_data_found.assert_any_call(1, True, f"{self.full_tomo_path}/{DATA_PATH}", self.data_array.shape)

    def test_images_found_indicated_on_view(self):
        self.nexus_loader.scan_nexus_file()
        self.view.set_images_found(0, True, self.sample.shape)
        self.view.set_images_found(1, True, self.flat_before.shape)
        self.view.set_images_found(2, True, self.flat_after.shape)
        self.view.set_images_found(3, True, self.dark_before.shape)
        self.view.set_images_found(4, True, self.dark_after.shape)

    def test_open_nexus_file_in_read_mode(self):
        self.view.filePathLineEdit.text.return_value = expected_file_path = "some_file_path"
        del self.nexus[self.full_tomo_path]  # Prevent it from doing the full operation
        self.nexus_loader.scan_nexus_file()
        self.nexus_load_mock.assert_called_once_with(expected_file_path, "r")

    def test_complete_file_returns_expected_dataset_and_title(self):
        self.nexus_loader.scan_nexus_file()
        dataset, title = self.nexus_loader.get_dataset()
        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(title, self.title)
        self.assertEqual(dataset.sample.pixel_size, self.expected_pixel_size)

    def test_dataset_arrays_match_image_key(self):
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        np.testing.assert_array_almost_equal(dataset.flat_before.data, self.flat_before)
        np.testing.assert_array_almost_equal(dataset.dark_before.data, self.dark_before)
        np.testing.assert_array_almost_equal(dataset.sample.data, self.sample)
        np.testing.assert_array_almost_equal(dataset.dark_after.data, self.dark_after)
        np.testing.assert_array_almost_equal(dataset.flat_after.data, self.flat_after)

    def test_no_flat_before_data(self):
        self.replace_values_in_image_key("Flat Before", 0)
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.flat_before)
        self.view.set_images_found.assert_any_call(1, False, (0, 10, 10))

    def test_no_dark_before_data(self):
        self.replace_values_in_image_key("Dark Before", 0)
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.dark_before)
        self.view.set_images_found.assert_any_call(3, False, (0, 10, 10))

    def test_no_flat_after_data(self):
        self.replace_values_in_image_key("Flat After", 0)
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.flat_after)
        self.view.set_images_found.assert_any_call(2, False, (0, 10, 10))

    def test_no_dark_after_data(self):
        self.replace_values_in_image_key("Dark After", 0)
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.dark_after)
        self.view.set_images_found.assert_any_call(4, False, (0, 10, 10))

    def test_no_projection_data(self):
        self.replace_values_in_image_key("Projections", 1)
        missing_string = _missing_data_message("projection images")
        with self.assertLogs(nexus_logger, level="ERROR") as log_mock:
            self.nexus_loader.scan_nexus_file()
        self.assertIn(missing_string, log_mock.output[0])
        self.view.show_missing_data_error.assert_called_once_with(missing_string)
        self.view.disable_ok_button.assert_called_once()
        self.view.set_images_found.assert_called_once_with(0, False, (0, 10, 10))

    def test_use_flat_before_data_is_false(self):
        self.view.checkboxes["Flat Before"].isChecked.return_value = False
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.flat_before)

    def test_use_dark_before_data_is_false(self):
        self.view.checkboxes["Dark Before"].isChecked.return_value = False
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.dark_before)

    def test_use_flat_after_data_is_false(self):
        self.view.checkboxes["Flat After"].isChecked.return_value = False
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.flat_after)

    def test_use_dark_after_data_is_false(self):
        self.view.checkboxes["Dark After"].isChecked.return_value = False
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        self.assertIsNone(dataset.dark_after)

    def test_dataset_has_expected_pixel_depth(self):
        depths = ["float32", "float64"]
        self.nexus_loader.scan_nexus_file()
        for depth in depths:
            self.view.pixelDepthComboBox.currentText.return_value = depth
            with self.subTest(depth=depth):
                dataset = self.nexus_loader.get_dataset()[0]
                self.assertEqual(dataset.sample.dtype, np.dtype(depth))
                self.assertEqual(dataset.flat_before.dtype, np.dtype(depth))
                self.assertEqual(dataset.dark_before.dtype, np.dtype(depth))
                self.assertEqual(dataset.dark_after.dtype, np.dtype(depth))
                self.assertEqual(dataset.flat_after.dtype, np.dtype(depth))

    def test_no_title_in_nexus_file(self):
        del self.tomo_entry["title"]
        self.nexus_loader.scan_nexus_file()
        assert self.nexus_loader.get_dataset()[1] == "NeXus Data"

    def test_image_names(self):
        self.nexus_loader.scan_nexus_file()
        dataset = self.nexus_loader.get_dataset()[0]
        assert dataset.sample.filenames[0] == "Projections " + self.title
        assert dataset.flat_before.filenames[0] == "Flat Before " + self.title
        assert dataset.dark_before.filenames[0] == "Dark Before " + self.title
        assert dataset.dark_after.filenames[0] == "Dark After " + self.title
        assert dataset.flat_after.filenames[0] == "Flat After " + self.title
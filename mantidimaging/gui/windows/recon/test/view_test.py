import unittest
from unittest import mock

from mantidimaging.core.utility.data_containers import ScalarCoR, Degrees, Slope
from mantidimaging.gui.windows.main import MainWindowView
from mantidimaging.gui.windows.recon import ReconstructWindowView
from mantidimaging.test_helpers import start_qapplication

from mantidimaging.core.utility.version_check import versions
versions._use_test_values()


@start_qapplication
class ReconstructWindowViewTest(unittest.TestCase):
    def setUp(self) -> None:
        with mock.patch("mantidimaging.gui.windows.main.view.WelcomeScreenPresenter"):
            with mock.patch("mantidimaging.gui.windows.main.view.has_other_shared_arrays", return_value=False):
                self.main_window = MainWindowView()
        self.view = ReconstructWindowView(self.main_window)
        self.view.presenter = self.presenter = mock.MagicMock()
        self.view.image_view = self.image_view = mock.MagicMock()
        self.view.tableView = self.tableView = mock.Mock()
        self.view.resultCor = self.resultCor = mock.Mock()
        self.view.resultTilt = self.resultTilt = mock.Mock()
        self.view.resultSlope = self.resultSlope = mock.Mock()

    def test_on_row_change(self):
        pass

    def test_check_stack_for_invalid_180_deg_proj(self):
        pass

    @mock.patch("mantidimaging.gui.windows.recon.view.QMessageBox")
    def test_warn_user(self, qmessagebox_mock):
        warning_title = "warning title"
        warning_message = "warning message"
        self.view.warn_user(warning_title, warning_message)
        qmessagebox_mock.warning.assert_called_once_with(self.view, warning_title, warning_message)

    def test_remove_selected_cor(self):
        assert self.view.remove_selected_cor() == self.tableView.removeSelectedRows.return_value

    def test_clear_cor_table(self):
        assert self.view.clear_cor_table() == self.tableView.model.return_value.removeAllRows.return_value

    def test_cor_table_model(self):
        pass

    def test_set_results(self):
        cor_val = 20
        tilt_val = 30
        slope_val = 40
        cor = ScalarCoR(cor_val)
        tilt = Degrees(tilt_val)
        slope = Slope(slope_val)

        self.view.set_results(cor, tilt, slope)
        assert self.view.rotation_centre == cor_val
        assert self.view.tilt == tilt_val
        assert self.view.slope == slope_val
        self.image_view.set_tilt.assert_called_once_with(tilt)

    def test_preview_image_on_button_press(self):
        event_mock = mock.Mock()
        event_mock.button = 1
        event_mock.ydata = ydata = 20.3

        self.view.preview_image_on_button_press(event_mock)
        self.presenter.set_preview_slice_idx.assert_called_once_with(int(ydata))

    def test_no_preview_image_on_button_press(self):
        event_mock = mock.Mock()
        event_mock.button = 2
        event_mock.ydata = 20.3

        self.view.preview_image_on_button_press(event_mock)
        self.presenter.set_preview_slice_idx.assert_not_called()

    def test_update_projection(self):
        image_data = mock.Mock()
        preview_slice_idx = 13
        tilt_angle = Degrees(30)

        self.view.previewSliceIndex = preview_slice_index_mock = mock.Mock()
        self.view.update_projection(image_data, preview_slice_idx, tilt_angle)

        preview_slice_index_mock.setValue.assert_called_once_with(preview_slice_idx)
        self.image_view.update_projection.assert_called_once_with(image_data, preview_slice_idx, tilt_angle)

    def test_update_sinogram(self):
        image_data = mock.Mock()
        self.view.update_sinogram(image_data)
        self.image_view.update_sinogram.assert_called_once_with(image_data)

    def test_update_recon_preview(self):
        image_data = mock.Mock()
        refresh_recon_slice_histogram = True

        self.view.update_recon_preview(image_data, refresh_recon_slice_histogram)
        self.image_view.update_recon.assert_called_once_with(image_data, refresh_recon_slice_histogram)

    def test_reset_image_recon_preview(self):
        self.view.reset_image_recon_preview()
        self.image_view.clear_recon.assert_called_once()

    def test_reset_slice_and_tilt(self):
        slice_index = 5
        self.view.reset_slice_and_tilt(slice_index)
        self.image_view.reset_slice_and_tilt.assert_called_once_with(slice_index)

    def test_on_table_row_count_changed(self):
        self.tableView.model.return_value.empty = empty = False
        self.view.removeBtn = remove_button_mock = mock.Mock()
        self.view.clearAllBtn = clear_all_button_mock = mock.Mock()
        self.view.on_table_row_count_change()

        remove_button_mock.setEnabled.assert_called_once_with(not empty)
        clear_all_button_mock.setEnabled.assert_called_once_with(not empty)

    def test_add_cor_table_row(self):
        row = 3
        slice_index = 4
        cor = 5.0

        self.view.add_cor_table_row(row, slice_index, cor)

        self.tableView.model.return_value.appendNewRow.assert_called_once_with(row, slice_index, cor)
        self.tableView.selectRow.assert_called_once_with(row)

    def test_rotation_centre_property(self):
        assert self.view.rotation_centre == self.resultCor.value.return_value

    def test_rotation_centre_setter(self):
        value = 16.3
        self.view.rotation_centre = value
        self.resultCor.setValue.assert_called_once_with(value)

    def test_tilt_property(self):
        assert self.view.tilt == self.resultTilt.value.return_value

    def test_tilt_setter(self):
        value = 123.45
        self.view.tilt = value
        self.resultTilt.setValue.assert_called_once_with(value)

    def test_slope_property(self):
        assert self.view.slope == self.resultSlope.value.return_value

    def test_slope_setter(self):
        value = 123.45
        self.view.slope = value
        self.resultSlope.setValue.assert_called_once_with(value)

    def test_max_proj_angle(self):
        self.view.maxProjAngle = max_proj_angle_mock = mock.Mock()
        assert self.view.max_proj_angle == max_proj_angle_mock.value.return_value

    def test_algorithm_name(self):
        self.view.algorithmName = algorithm_name_mock = mock.Mock()
        assert self.view.algorithm_name == algorithm_name_mock.currentText.return_value

    def test_filter_name(self):
        pass

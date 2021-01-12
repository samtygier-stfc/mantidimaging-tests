import unittest
from unittest import mock

from mantidimaging.core.utility.data_containers import ScalarCoR, ReconstructionParameters, Degrees
from mantidimaging.gui.dialogs.cor_inspection import CORInspectionDialogPresenter
import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.gui.dialogs.cor_inspection.types import ImageType


class CORInspectionDialogPresenterTest(unittest.TestCase):
    @mock.patch("mantidimaging.gui.dialogs.cor_inspection.CORInspectionDialogModel")
    def setUp(self, model) -> None:
        self.view = mock.MagicMock()
        self.model = model
        self.recon_params = ReconstructionParameters("", "", 0, ScalarCoR(2), Degrees(2), 2, 2)
        self.presenter = CORInspectionDialogPresenter(self.view, th.generate_images(), 5, ScalarCoR(2),
                                                      self.recon_params, False)

    def test_init_sets_get_title(self):
        with mock.patch("mantidimaging.gui.dialogs.cor_inspection.CORInspectionDialogModel"):
            presenter = CORInspectionDialogPresenter(self.view, th.generate_images(), 5, ScalarCoR(2),
                                                     self.recon_params, True)
            assert "Iterations" in presenter.get_title(ImageType.CURRENT)

            presenter = CORInspectionDialogPresenter(self.view, th.generate_images(), 5, ScalarCoR(2),
                                                     self.recon_params, False)
            assert "COR" in presenter.get_title(ImageType.CURRENT)

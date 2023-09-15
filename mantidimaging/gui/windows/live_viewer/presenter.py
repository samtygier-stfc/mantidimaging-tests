# Copyright (C) 2023 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from logging import getLogger

from imagecodecs._deflate import DeflateError
from tifffile import tifffile, TiffFileError

from mantidimaging.gui.mvp_base import BasePresenter
from mantidimaging.gui.windows.live_viewer.model import LiveViewerWindowModel, Image_Data

if TYPE_CHECKING:
    from mantidimaging.gui.windows.live_viewer.view import LiveViewerWindowView  # pragma: no cover
    from mantidimaging.gui.windows.main.view import MainWindowView  # pragma: no cover

logger = getLogger(__name__)


class LiveViewerWindowPresenter(BasePresenter):
    """
    The presenter for the Live Viewer window.

    This presenter is responsible for handling user interaction with the view and
    updating the model and view accordingly to look after the state of the window.
    """
    view: LiveViewerWindowView
    model: LiveViewerWindowModel

    def __init__(self, view: LiveViewerWindowView, main_window: MainWindowView):
        super().__init__(view)

        self.view = view
        self.main_window = main_window
        self.model = LiveViewerWindowModel(self)

    def close(self) -> None:
        """Close the window."""
        self.model.close()
        self.model = None  # type: ignore # Presenter instance to be destroyed -type can be inconsistent
        self.view = None  # type: ignore # Presenter instance to be destroyed -type can be inconsistent

    def set_dataset_path(self, path: Path) -> None:
        """Set the path to the dataset."""
        self.model.path = path

    def clear_label(self) -> None:
        """Clear the label."""
        self.view.label_active_filename.setText("")

    def handle_deleted(self) -> None:
        """Handle the deletion of the image."""
        self.view.remove_image()
        self.clear_label()
        self.view.live_viewer.z_slider.set_range(0, 1)

    def update_image_list(self, images_list: list[Image_Data]) -> None:
        """Update the image in the view."""
        if not images_list:
            self.handle_deleted()
            return

        self.view.live_viewer.z_slider.set_range(0, len(images_list) - 1)
        self.view.set_image_index(len(images_list) - 1)

    def select_image(self, index: int) -> None:
        if not self.model.images:
            return
        selected_image = self.model.images[index]
        self.view.label_active_filename.setText(selected_image.image_name)

        try:
            with tifffile.TiffFile(selected_image.image_path) as tif:
                image_data = tif.asarray()
        except (IOError, KeyError, ValueError, TiffFileError, DeflateError) as error:
            logger.error("%s reading image: %s: %s", type(error).__name__, selected_image.image_path, error)
            self.view.remove_image()
            return
        if image_data.size == 0:
            logger.error("reading image: %s: Image has zero size", selected_image.image_path)
            return

        self.view.show_most_recent_image(image_data)

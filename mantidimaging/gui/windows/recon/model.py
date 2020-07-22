from logging import getLogger
from typing import Optional, Tuple, List
from typing import TYPE_CHECKING

import numpy as np

from mantidimaging.core.cor_tilt import (update_image_operations)
from mantidimaging.core.reconstruct import get_reconstructor_for
from mantidimaging.core.reconstruct.astra_recon import allowed_recon_kwargs as astra_allowed_kwargs, AstraRecon
from mantidimaging.core.reconstruct.tomopy_recon import allowed_recon_kwargs as tomopy_allowed_kwargs
from mantidimaging.core.utility.data_containers import ScalarCoR, Degrees, Slope, ProjectionAngles, \
    ReconstructionParameters
from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.core.utility.projection_angles import (generate as generate_projection_angles)
from mantidimaging.gui.windows.recon.point_table_model import CorTiltPointQtModel

if TYPE_CHECKING:
    from mantidimaging.gui.windows.stack_visualiser import StackVisualiserView

LOG = getLogger(__name__)


class ReconstructWindowModel(object):
    proj_angles: Optional[ProjectionAngles]

    def __init__(self, data_model: CorTiltPointQtModel):
        self.stack: Optional['StackVisualiserView'] = None
        self.preview_projection_idx = 0
        self.preview_slice_idx = 0
        self.selected_row = 0
        self.projection_indices = None
        self.data_model = data_model
        self.last_result = None
        self._last_cor = ScalarCoR(0.0)

    @property
    def last_cor(self):
        return self._last_cor

    @last_cor.setter
    def last_cor(self, value):
        self._last_cor = value

    @property
    def has_results(self):
        return self.data_model.has_results

    def get_results(self) -> Tuple[ScalarCoR, Degrees, Slope]:
        return self.data_model.cor, self.data_model.angle_in_degrees, self.data_model.gradient

    @property
    def images(self):
        return self.stack.presenter.images if self.stack else None

    @property
    def num_points(self):
        return self.data_model.num_points

    def initial_select_data(self, stack):
        self.data_model.clear_results()

        self.stack = stack
        slice_idx, _ = self.find_initial_cor()

        self.preview_projection_idx = 0
        self.preview_slice_idx = slice_idx

        if stack is not None:
            self.proj_angles = generate_projection_angles(360, self.images.num_projections)

    def find_initial_cor(self) -> [int, ScalarCoR]:
        if self.images is not None:
            first_slice_to_recon = self._get_initial_slice_index()
            # Getting the middle of the image is probably closer than Tomopy's CoR from what I've seen
            # and certainly much faster. IF a better method is found it might be worth going to it instead
            cor = ScalarCoR(self.images.width // 2)
            self.last_cor = cor

            return first_slice_to_recon, cor
        return 0, ScalarCoR(0)

    def _get_initial_slice_index(self):
        first_slice_to_recon = self.images.num_sinograms // 2
        return first_slice_to_recon

    def do_fit(self):
        # Ensure we have some sample data
        if self.stack is None:
            raise ValueError('No image stack is provided')

        self.data_model.linear_regression()
        update_image_operations(self.images, self.data_model)

        # Cache last result
        self.last_result = self.data_model.stack_properties

        # Async task needs a non-None result of some sort
        return True

    def run_preview_recon(self, slice_idx, cor: ScalarCoR, recon_params: ReconstructionParameters):
        # Ensure we have some sample data
        if self.images is None:
            return None

        # Perform single slice reconstruction
        reconstructor = get_reconstructor_for(recon_params.algorithm)
        return reconstructor.single(self.images, slice_idx, cor, self.proj_angles, recon_params)

    def run_full_recon(self, recon_params: ReconstructionParameters, progress: Progress):
        reconstructor = get_reconstructor_for(recon_params.algorithm)
        # get the image height based on the current ROI
        return reconstructor.full(self.images, self.data_model.get_all_cors_from_regression(self.images.height),
                                  self.proj_angles, recon_params, progress)

    @property
    def tilt_angle(self) -> Optional[Degrees]:
        if self.data_model.has_results:
            return self.data_model.angle_in_degrees

    @property
    def cors(self):
        return self.data_model.cors

    @property
    def slices(self):
        return self.data_model.slices

    @staticmethod
    def load_allowed_recon_kwargs():
        d = tomopy_allowed_kwargs()
        d.update(astra_allowed_kwargs())
        return d

    @staticmethod
    def get_allowed_filters(alg_name: str):
        reconstructor = get_reconstructor_for(alg_name)
        return reconstructor.allowed_filters()

    def get_me_a_cor(self, cor=None):
        if cor is not None:
            # a cor has been passed in!
            return cor

        if self.has_results:
            cor = self.get_cor_for_slice_from_regression()
        elif self.last_cor is not None:
            # otherwise just use the last cached CoR
            cor = self.last_cor
        return cor

    def get_cor_for_slice_from_regression(self) -> ScalarCoR:
        return ScalarCoR(self.data_model.get_cor_from_regression(self.preview_slice_idx))

    def reset_selected_row(self):
        self.selected_row = 0

    def set_precalculated(self, cor: ScalarCoR, tilt: Degrees):
        self.data_model.set_precalculated(cor, tilt)
        self.last_result = self.data_model.stack_properties

    def is_current_stack(self, stack):
        return self.stack == stack

    def get_slice_indices(self, num_cors: int) -> Tuple[int, List[int]]:
        # used to crop off 20% off the top and bottom, which is usually noise/empty
        remove_a_bit = self.images.height * 0.2
        slices: List[int] = np.linspace(remove_a_bit, self.images.height - remove_a_bit, num=num_cors, dtype=np.int32)
        return self.selected_row, slices

    def auto_find_cors_for_slices(self, slices: List[int], recon_params: ReconstructionParameters,
                                  progress: Progress) -> List[float]:

        progress = Progress.ensure_instance(progress, num_steps=len(slices))
        progress.update(0, msg=f"Calculating COR for slice {slices[0]}")
        cors = []
        for slice in slices:
            cor = AstraRecon.find_cor(self.images, slice, self.images.width / 2, self.proj_angles, recon_params)
            cors.append(cor)
            progress.update(msg=f"Calculating COR for slice {slice}")
        return cors
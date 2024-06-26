# Copyright (C) 2024 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
from __future__ import annotations

import numpy as np


class UnitConversion:
    # target_to_camera_dist = 56 m taken from https://scripts.iucr.org/cgi-bin/paper?S1600576719001730
    neutron_mass: float = 1.674927211e-27  # [kg]
    planck_h: float = 6.62606896e-34  # [JHz-1]
    angstrom: float = 1e-10  # [m]
    mega_electro_volt: float = 1.60217662e-19 / 1e6

    def __init__(self, data_to_convert: np.ndarray, target_to_camera_dist: float = 56) -> None:
        self.tof_data_to_convert = data_to_convert
        self.target_to_camera_dist = target_to_camera_dist
        self.velocity = self.target_to_camera_dist / self.tof_data_to_convert

    def tof_seconds_to_wavelength(self) -> np.ndarray:
        wavelength = self.planck_h / (self.neutron_mass * self.velocity)
        wavelength_angstroms = wavelength / self.angstrom
        return wavelength_angstroms

    def tof_seconds_to_energy(self) -> np.ndarray:
        energy = self.neutron_mass * self.velocity / 2
        energy_evs = energy / self.mega_electro_volt
        return energy_evs

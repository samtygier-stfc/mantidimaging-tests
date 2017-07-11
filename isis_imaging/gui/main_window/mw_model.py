from __future__ import (absolute_import, division, print_function)

import uuid

import numpy as np
from PyQt5.QtWidgets import QDockWidget

from isis_imaging.core.io import loader, saver
from isis_imaging.gui.stack_visualiser.sv_view import StackVisualiserView


class MainWindowModel(object):
    def __init__(self, config):
        super(MainWindowModel, self).__init__()
        self.config = config

        self.active_stacks = {}

    def do_load_stack(self, sample_path, image_format, parallel_load, indices) -> np.ndarray:
        sample, _, _ = loader.load(
            sample_path,
            None,
            None,
            image_format,
            parallel_load=parallel_load,
            indices=indices)

        return sample

    def do_saving(self, stack_uuid, output_dir, name_prefix, image_format, overwrite, swap_axes, indices):
        self.get_stack_visualiser(stack_uuid).apply_to_data(
            saver.save,
            output_dir=output_dir,
            name_prefix=name_prefix,
            swap_axes=swap_axes,
            overwrite_all=overwrite,
            out_format=image_format,
            indices=indices)

    def create_title(self, file):
        # TODO can add more processing of the file, e.g. remove the numbers from the file and convert to
        # 'image_name_xxx' or simply strip all numbers, but we can't be sure the last underscore in the string
        # will be right before the number
        return file

    def stack_list(self) -> list:
        stacks = []
        for stack_uuid, widget in self.active_stacks.items():
            # ask the widget for its current title
            current_name = widget.windowTitle()
            # append the UUID and user friendly name
            stacks.append((stack_uuid, current_name))

        # sort by user friendly name
        return sorted(stacks, key=lambda x: x[1])

    def stack_names(self) -> list:
        # unpacks the tuple and only gives the correctly sorted human readable names
        return zip(*self.stack_list())[1]

    def add_stack(self, stack_visualiser: StackVisualiserView, dock_widget: QDockWidget):
        # generate unique ID for this stack
        stack_visualiser.uuid = uuid.uuid1()
        self.active_stacks[stack_visualiser.uuid] = dock_widget
        print("Active stacks", self.active_stacks)

    def get_stack(self, stack_uuid) -> QDockWidget:
        """
        :param stack_uuid: The unique ID of the stack that will be retrieved.
        :return The QDockWidget that contains the Stack Visualiser. For direct access to the
                Stack Visualiser widget use get_stack_visualiser
        """
        return self.active_stacks[stack_uuid]

    def get_stack_visualiser(self, stack_uuid) -> StackVisualiserView:
        """
        :param stack_uuid: The unique ID of the stack that will be retrieved.
        :return The Stack Visualiser widget that contains the data.
        """
        return self.active_stacks[stack_uuid].widget()

    def do_remove_stack(self, stack_uuid):
        """
        Removes the stack from the active_stacks dictionary.

        :param stack_uuid: The unique ID of the stack that will be removed.
        """
        del self.active_stacks[stack_uuid]

    def apply_to_data(self, stack_uuid, function):
        self.get_stack_visualiser(stack_uuid).apply_to_data(function)

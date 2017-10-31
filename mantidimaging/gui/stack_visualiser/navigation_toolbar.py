from __future__ import absolute_import, division, print_function

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

from .presenter import Notification


class StackNavigationToolbar(NavigationToolbar2QT):

    # See [Matplotlib]/lib/matplotlib/backend_bases.py
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
        (None, None, None, None),
        ('Previous Slice', 'Scroll to the previous image in the stack',
            'back', 'scroll_stack_back'),
        ('Next Slice', 'Scroll to the next image in the stack', 'forward',
            'scroll_stack_forward'),
      )

    stack_visualiser = None

    def scroll_stack_back(self):
        if self.stack_visualiser:
            self.stack_visualiser.presenter.notify(Notification.SCROLL_DOWN)

    def scroll_stack_forward(self):
        if self.stack_visualiser:
            self.stack_visualiser.presenter.notify(Notification.SCROLL_UP)
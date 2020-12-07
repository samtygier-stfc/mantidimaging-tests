# Copyright (C) 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

from PyQt5.QtCore import QSettings
from logging import getLogger

from mantidimaging.gui.mvp_base.presenter import BasePresenter
from mantidimaging.gui.windows.welcome_screen.view import WelcomeScreenView
from mantidimaging.core.utility.version_check import versions

LOG = getLogger(__name__)

WELCOME_LINKS = [
    ["Homepage", "https://github.com/mantidproject/mantidimaging"],
    ["Documentation", "https://mantidproject.github.io/mantidimaging/index.html"],
]


class WelcomeScreenPresenter(BasePresenter):
    def __init__(self, parent=None, view=None):
        if view is None:
            view = WelcomeScreenView(parent, self)

        super(WelcomeScreenPresenter, self).__init__(view)
        self.settings = QSettings()
        self.link_count = 0

        self.do_set_up()

    def do_set_up(self):
        self.view.set_version_label(f"Mantid Imaging {versions.get_version()}")
        self.set_up_links()
        self.set_up_show_at_start()
        self.check_issues()

    def show(self):
        self.view.show()

    @staticmethod
    def show_at_start_enabled():
        settings = QSettings()
        return settings.value("welcome_screen/show_at_start", defaultValue=True, type=bool)

    def set_up_links(self):
        for link_name, url in WELCOME_LINKS:
            self.add_link(link_name, url)

    def add_link(self, link_name, url):
        rich_text = f'<a href="{url}">{link_name}</a>'
        self.view.add_link(rich_text, self.link_count)
        self.link_count += 1

    def set_up_show_at_start(self):
        show_at_start = WelcomeScreenPresenter.show_at_start_enabled()
        self.view.set_show_at_start(show_at_start)
        self.show_at_start_changed()

    def show_at_start_changed(self):
        show_at_start = self.view.get_show_at_start()
        self.settings.setValue("welcome_screen/show_at_start", show_at_start)

    def check_issues(self):
        if not versions.is_conda_uptodate():
            msg, detailed = versions.conda_update_message()
            self.view.add_issue(msg)
            LOG.info(detailed)

"""Open a terminal from Mamba text editor"""
__pluginname__ = "Open Terminal"
__author__ = "Marco Laspe"
__credits__ = ["Andrei Kopats", "Bryan A. Jones"]
__license__ = "GPL3"
__version__ = "0.1.0"
__maintainer__ = "Marco Laspe"
__email__ = "marco@rockiger.com"
__status__ = "Beta"
# This plugin is a copy of the Enki repl plugin
# https://github.com/andreikop/enki/tree/master/enki/plugins/openterm.py

import subprocess
import platform
import os.path
import os

from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, \
    QLabel, QLineEdit, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon

from enki.core.core import core
from enki.core.uisettings import TextOption


if platform.system() == 'Windows':
    ACTION_TEXT = "Command Prompt"
else:
    ACTION_TEXT = "Terminal"


import os.path
import os


def _commandExists(program):
    def _isExe(filePath):
        return os.path.isfile(filePath) and os.access(filePath, os.X_OK)

    for path in os.environ.get("PATH", '').split(os.pathsep):
        path = path.strip('"')
        exeFile = os.path.join(path, program)
        if _isExe(exeFile):
            return True

    return False


class SettingsPage(QWidget):
    """Settings page for OpenTerm plugin
    """

    def __init__(self, parent, autodetectedCommand):
        QWidget.__init__(self, parent)

        text = "<h2>Open Terminal</h2>" +\
               "<h3>Terminal emulator command.</h3>" + \
               "<p>Leave empty to autodetect.<br/>" + \
               "Autodetected value is <i>{}</i></p>".format(autodetectedCommand)
        self._label = QLabel(text, self)
        self.edit = QLineEdit(self)

        self._vLayout = QVBoxLayout(self)
        self._vLayout.addWidget(self._label)
        self._vLayout.addWidget(self.edit)
        self._vLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))


class Plugin:

    def __init__(self):
        self._addAction()
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

    def terminate(self):
        core.actionManager().removeAction('mPlugins/aOpenTerm')
        core.uiSettingsManager().aboutToExecute.disconnect(self._onSettingsDialogAboutToExecute)

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        """
        page = SettingsPage(dialog, self._chooseDefaultTerminal())
        icon = QIcon(os.path.join(os.path.dirname(__file__), 'terminal.svg'))
        dialog.appendPage(ACTION_TEXT, page,
                          QIcon.fromTheme('utilities-terminal',
                                          QIcon(icon)))

        # Options
        dialog.appendOption(TextOption(dialog, core.config(), "OpenTerm/Term", page.edit))

    def _chooseDefaultTerminal(self):
        if platform.system() == 'Windows':
            commands = ['powershell.exe',
                        'cmd.exe']
        else:
            commands = ['x-terminal-emulator',
                        'mate-terminal',
                        'gnome-terminal',
                        'konsole',
                        'qterminal',
                        'xterm']

        for cmd in commands:
            if _commandExists(cmd):
                return cmd
        else:
            return None

    def _addAction(self):
        """Add action to main menu
        """
        action = core.actionManager().addAction("mPlugins/aOpenTerm",
                                                ACTION_TEXT,
                                                QIcon.fromTheme('utilities-terminal'))
        core.actionManager().setDefaultShortcut(action, "Ctrl+T")
        action.triggered.connect(self._openTerm)

    def _openTerm(self):
        """Handler for main menu action
        """
        term = core.config()["OpenTerm"]["Term"]
        if not term:
            term = self._chooseDefaultTerminal()

        if not term:
            return

        if term in ['konsole', 'qterminal']:
            term = [term, '--workdir', os.getcwd()]

        try:
            subprocess.Popen(term, cwd=os.getcwd())
        except Exception as ex:
            QMessageBox.information(core.mainWindow(),
                                    "Failed to open terminal",
                                    "Enki was unable to run '{0}': {1}".format(term, str(ex)))

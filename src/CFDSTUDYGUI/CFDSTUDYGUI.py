# This file is part of code_saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2025 EDF S.A.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.

# --- should be done at the very first to avoid interference with logging.basicConfig() from code_saturne
import logging
from cfdstudy import initlog
initlog.setDebug()
# ---

from cfdstudy.clientgui import getClientGui
from cfdstudy import clientgui
import salome


salome.salome_init()


def salome_init(studyId, embedded):
    """
    called by GUI (SALOME_PyQt)
    """
    logging.debug("salome_init %s %s", studyId, embedded)


def setWorkSpace(pyws):
    """
    called by GUI (SALOME_PyQt)
    """
    logging.debug("setWorkSpace")


def initialize():
    """
    called by GUI (SALOME_PyQt)
    """
    logging.debug("initialize")
    getClientGui().initialize()


def windows():
    """
    called by GUI (SALOME_PyQt)

    :return: required dockable windows list from the Python module = map
    :rtype: map{int:int}
    """
    logging.debug("windows")
    return {}


def views():
    """
    called by GUI (SALOME_PyQt)
    get compatible view windows types from the Python module
    """
    logging.debug("views")
    return [clientgui.getCfdStudyViewType()]


def activate():
    """
    called by GUI (SALOME_PyQt)
    called when module is activated

    :return: True if activating is successful and False otherwise
    :rtype: boolean
    """
    logging.debug("activate")
    return getClientGui().activate()


def setSettings():
    """
    called by GUI (SALOME_PyQt). Obsolete.
    """
    logging.debug("setSettings")


def deactivate():
    """
    called by GUI (SALOME_PyQt).
    called when module is deactivated
    """
    logging.debug("deactivate")
    getClientGui().deactivate()


def closeStudy(studyID):
    """
    called by GUI (SALOME_PyQt).
    called when active study is closed

    :param studyID: SALOME Study identifiant
    :type studyID: int
    """
    logging.debug("closeStudy: %s", studyID)
    getClientGui().closeStudy()

    # """
    # called by GUI (SALOME_PyQt).
    # called when active study is closed
    # """


def preferenceChanged(section, setting):
    """
    called by GUI (SALOME_PyQt).
     """
    logging.debug("preferenceChanged %s %s", section, setting)


def activeStudyChanged():
    """
    called by GUI (SALOME_PyQt).
    called when active study is changed.
    """
    logging.debug("activeStudyChanged")


def OnGUIEvent(commandID):
    """
    called by GUI (SALOME_PyQt).
    process gui action
    """
    logging.debug("OnGUIEvent: %s", commandID)
    getClientGui().OnGUIEvent(commandID)


def onSelectionUpdated(entryList):
    """
    called by GUI (SALOME_PyQt).
    called when selection is modified on other views (modules, viewers...)
    """
    logging.debug("onSelectionUpdated: %s", entryList)
    getClientGui().onSelectionUpdated(entryList)


def createPopupMenu(popup, context):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("createPopupMenu")


def createPreferences():
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("createPreferences")
    getClientGui().createPreferences()

def activeViewChanged(viewId):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("activeViewChanged %s", viewId)


def viewTryClose(viewId):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("viewTryClose %s", viewId)


def viewClosed(viewId):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("viewClosed %s", viewId)


def viewCloned(viewId):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("viewCloned %s", viewId)


def saveFiles(directory, url):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("saveFiles: %s %s", directory, url)
    return getClientGui().saveFiles(directory, url)


def openFiles(files, url):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("openFiles:  %s %s", files, url)
    return getClientGui().openFiles(files, url)


def dumpStudy(files):
    """
    called by GUI (SALOME_PyQt).
    """
    logging.debug("dumpStudy:  %s", files)

    # isDraggable, what
    # isDropAccepted, where
    # dropObjects, Osii
    # engineIOR
    # onObjectBrowserClicked, si


# def publishCase(CaseName, meshCond, meshRay):
#     """
#     call from Saturne GUI: SATURNE_IHMCollector.PublishInSalome
#     publish case in SALOME study with the associated meshes, and update the object browser
#     """
#     logging.debug("publishCase %s %s %s", CaseName, meshCond, meshRay)
#     getClientGui().publishCase(CaseName, meshCond, meshRay)

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

INCLUDE(UsePyQt)
INCLUDE(UseQtExt)

#additional include directories
INCLUDE_DIRECTORIES(
  ${QT_INCLUDES}
)

# --- scripts ---

# scripts / static
SET(_bin_SCRIPTS
  CFDSTUDYGUI.py
)

SET(_lib_SCRIPTS
  CFDSTUDYGUI_ActionsHandler.py
  CFDSTUDYGUI_Agents.py
  CFDSTUDYGUI_CommandMgr.py
  CFDSTUDYGUI_Commons.py
  CFDSTUDYGUI_DataModel.py
  CFDSTUDYGUI_DesktopMgr.py
  CFDSTUDYGUI_DialogCollector.py
  CFDSTUDYGUI_Management.py
  CFDSTUDYGUI_Message.py
  CFDSTUDYGUI_SolverGUI.py
  clientgui.py
  CLSMainWindow.py
  constants.py
  initlog.py
  __init__.py
  CFDSTUDYGUI.py
  utilstudy.py
)


# --- resources ---

#resource files / to be processed by lrelease
SET(_ts_RESOURCES
  CFDSTUDY_msg_en.ts
  CFDSTUDY_msg_fr.ts
  CFDSTUDY_icons.ts
  CFDSTUDY_images.ts
)

# uic files / to be processed by pyuic
SET(_pyuic_files
  mw_cfdstudy.ui
  ECSConversionDialog.ui
  GUIActivationDialog.ui
  InfoDialog.ui
  SetTreeLocationDialog.ui
  CFDSTUDYGUI_QProcessDialog.ui
)

# scripts / pyuic wrappings
PYQT_WRAP_UIC(_pyuic_SCRIPTS ${_pyuic_files})

# --- rules ---

SALOME_INSTALL_SCRIPTS("${_bin_SCRIPTS}" ${SALOME_INSTALL_SCRIPT_PYTHON})
SALOME_INSTALL_SCRIPTS("${_pyuic_SCRIPTS}" ${SALOME_INSTALL_PYTHON}/cfdstudy)
SALOME_INSTALL_SCRIPTS("${_lib_SCRIPTS}" ${SALOME_INSTALL_PYTHON}/cfdstudy)

QT_INSTALL_TS_RESOURCES("${_ts_RESOURCES}" "${SALOME_CFDSTUDY_INSTALL_RES_DATA}")

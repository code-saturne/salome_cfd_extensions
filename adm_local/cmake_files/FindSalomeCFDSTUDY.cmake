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

IF(NOT SalomeCFDSTUDY_FIND_QUIETLY)
  MESSAGE(STATUS "Looking for Salome CFDSTUDY ...")
ENDIF()

SET(CMAKE_PREFIX_PATH "${CFDSTUDY_ROOT_DIR}")
SALOME_FIND_PACKAGE(SalomeCFDSTUDY SalomeCFDSTUDY CONFIG)

IF(NOT SalomeCFDSTUDY_FIND_QUIETLY)
  MESSAGE(STATUS "Found Salome CFDSTUDY: ${CFDSTUDY_ROOT_DIR}")
ENDIF()

FOREACH(_res ${SalomeCFDSTUDY_EXTRA_ENV})
  SALOME_ACCUMULATE_ENVIRONMENT(${_res} "${SalomeCFDSTUDY_EXTRA_ENV_${_res}}")
ENDFOREACH()

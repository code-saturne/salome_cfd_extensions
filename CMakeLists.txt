# This file is part of code_saturne, a general-purpose CFD tool.

# Copyright (C) 1998-2025 EDF S.A.

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
CMAKE_MINIMUM_REQUIRED(VERSION 2.8.8 FATAL_ERROR)
PROJECT(SalomeCFDSTUDY C CXX)

# Ensure a proper linker behavior:
CMAKE_POLICY(SET CMP0003 NEW)

# Versioning
# ===========
# Project name, upper case
STRING(TOUPPER ${PROJECT_NAME} PROJECT_NAME_UC)

SET(${PROJECT_NAME_UC}_MAJOR_VERSION 8)
SET(${PROJECT_NAME_UC}_MINOR_VERSION 2)
SET(${PROJECT_NAME_UC}_PATCH_VERSION 0)
SET(${PROJECT_NAME_UC}_VERSION
  ${${PROJECT_NAME_UC}_MAJOR_VERSION}.${${PROJECT_NAME_UC}_MINOR_VERSION}.${${PROJECT_NAME_UC}_PATCH_VERSION})
SET(${PROJECT_NAME_UC}_VERSION_DEV 0)

# Common CMake macros
# ===================
SET(CONFIGURATION_ROOT_DIR $ENV{CONFIGURATION_ROOT_DIR} CACHE PATH "Path to the Salome CMake configuration files")
IF(EXISTS ${CONFIGURATION_ROOT_DIR})
  LIST(APPEND CMAKE_MODULE_PATH "${CONFIGURATION_ROOT_DIR}/cmake")
  INCLUDE(SalomeMacros)
ELSE()
  MESSAGE(FATAL_ERROR "We absolutely need the Salome CMake configuration files, please define CONFIGURATION_ROOT_DIR !")
ENDIF()

# Find KERNEL
# ===========
SET(KERNEL_ROOT_DIR $ENV{KERNEL_ROOT_DIR} CACHE PATH "Path to the Salome KERNEL")
IF(EXISTS ${KERNEL_ROOT_DIR})
  LIST(APPEND CMAKE_MODULE_PATH "${KERNEL_ROOT_DIR}/salome_adm/cmake_files")
  INCLUDE(SalomeMacros)
  FIND_PACKAGE(SalomeKERNEL REQUIRED)
ELSE(EXISTS ${KERNEL_ROOT_DIR})
  MESSAGE(FATAL_ERROR "We absolutely need a Salome KERNEL, please define KERNEL_ROOT_DIR")
ENDIF(EXISTS ${KERNEL_ROOT_DIR})

# Platform setup
# ==============
INCLUDE(SalomeSetupPlatform)   # From KERNEL
# Always build libraries as shared objects:
SET(BUILD_SHARED_LIBS TRUE)
# Local macros:
LIST(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/adm_local/cmake_files")

# User options
# ============
OPTION(SALOME_BUILD_TESTS "Build SALOME tests" ON)
# OPTION(SALOME_BUILD_DOC "Generate SALOME CFDSTUDY documentation" ON) #For use in the future

IF(SALOME_BUILD_TESTS)
  ENABLE_TESTING()
ENDIF()

##
## From KERNEL:
##
FIND_PACKAGE(SalomePythonInterp REQUIRED)
FIND_PACKAGE(SalomePythonLibs REQUIRED)

# Find GUI
# ===========
SET(GUI_ROOT_DIR $ENV{GUI_ROOT_DIR} CACHE PATH "Path to the Salome GUI")
IF(EXISTS ${GUI_ROOT_DIR})
   LIST(APPEND CMAKE_MODULE_PATH "${GUI_ROOT_DIR}/adm_local/cmake_files")
   FIND_PACKAGE(SalomeGUI REQUIRED)
   ADD_DEFINITIONS(${GUI_DEFINITIONS})
   INCLUDE_DIRECTORIES(${GUI_INCLUDE_DIRS})
 ELSE(EXISTS ${GUI_ROOT_DIR})
   MESSAGE(FATAL_ERROR "We absolutely need a Salome GUI, please define GUI_ROOT_DIR")
ENDIF(EXISTS ${GUI_ROOT_DIR})

##
## From GUI:
##
# Qt
FIND_PACKAGE(SalomeQt5 REQUIRED)
FIND_PACKAGE(SalomePyQt5 REQUIRED)

# Directories
# (default values taken from KERNEL)
# ===========
SET(SALOME_INSTALL_BINS "${SALOME_INSTALL_BINS}" CACHE PATH "Install path: SALOME binaries")
SET(SALOME_INSTALL_LIBS "${SALOME_INSTALL_LIBS}" CACHE PATH "Install path: SALOME libs")
SET(SALOME_INSTALL_HEADERS "${SALOME_INSTALL_HEADERS}" CACHE PATH "Install path: SALOME headers")
SET(SALOME_INSTALL_SCRIPT_SCRIPTS "${SALOME_INSTALL_SCRIPT_SCRIPTS}" CACHE PATH
   "Install path: SALOME scripts")
SET(SALOME_INSTALL_SCRIPT_DATA "${SALOME_INSTALL_SCRIPT_DATA}" CACHE PATH
   "Install path: SALOME script data")
SET(SALOME_INSTALL_SCRIPT_PYTHON "${SALOME_INSTALL_SCRIPT_PYTHON}" CACHE PATH
   "Install path: SALOME Python scripts")
SET(SALOME_INSTALL_APPLISKEL_SCRIPTS "${SALOME_INSTALL_APPLISKEL_SCRIPTS}" CACHE PATH
   "Install path: SALOME application skeleton - scripts")
SET(SALOME_INSTALL_APPLISKEL_PYTHON "${SALOME_INSTALL_APPLISKEL_PYTHON}" CACHE PATH
   "Install path: SALOME application skeleton - Python")
#SET(SALOME_INSTALL_PYTHON "${SALOME_INSTALL_PYTHON}" CACHE PATH "Install path: SALOME Python stuff")
#SET(SALOME_INSTALL_PYTHON_SHARED "${SALOME_INSTALL_PYTHON_SHARED}" CACHE PATH
#   "Install path: SALOME Python shared modules")
SET(SALOME_INSTALL_CMAKE_LOCAL "${SALOME_INSTALL_CMAKE_LOCAL}" CACHE PATH "Install path: SALOME CMake files")
SET(SALOME_INSTALL_AMCONFIG_LOCAL "${SALOME_INSTALL_AMCONFIG_LOCAL}" CACHE PATH
  "Install path: local SALOME config files (obsolete, to be removed)")

SET(SALOME_INSTALL_RES "${SALOME_INSTALL_RES}" CACHE PATH "Install path: SALOME resources")
SET(SALOME_INSTALL_DOC "${SALOME_INSTALL_DOC}" CACHE PATH "Install path: SALOME documentation")

# Specific to CFDSTUDY:
SET(SALOME_CFDSTUDY_INSTALL_RES_DATA "${SALOME_INSTALL_RES}/cfdstudy" CACHE PATH
    "Install path: SALOME CFDSTUDY specific data")

MARK_AS_ADVANCED(SALOME_INSTALL_BINS SALOME_INSTALL_LIBS SALOME_INSTALL_IDLS SALOME_INSTALL_HEADERS)
MARK_AS_ADVANCED(SALOME_INSTALL_SCRIPT_SCRIPTS SALOME_INSTALL_SCRIPT_DATA SALOME_INSTALL_SCRIPT_PYTHON)
MARK_AS_ADVANCED(SALOME_INSTALL_APPLISKEL_SCRIPTS  SALOME_INSTALL_APPLISKEL_PYTHON SALOME_INSTALL_CMAKE_LOCAL SALOME_INSTALL_RES)
MARK_AS_ADVANCED(SALOME_INSTALL_PYTHON SALOME_INSTALL_PYTHON_SHARED)
MARK_AS_ADVANCED(SALOME_INSTALL_AMCONFIG_LOCAL SALOME_INSTALL_DOC)
MARK_AS_ADVANCED(SALOME_CFDSTUDY_INSTALL_RES_DATA)

# Accumulate environment variables for CFDSTUDY module
SALOME_ACCUMULATE_ENVIRONMENT(PYTHONPATH NOCHECK ${CMAKE_INSTALL_PREFIX}/${SALOME_INSTALL_BINS})

# Sources
# ========

ADD_SUBDIRECTORY(adm_local)
ADD_SUBDIRECTORY(resources)
ADD_SUBDIRECTORY(src)
ADD_SUBDIRECTORY(bin)

# Configuration export
# (here only the level 1 prerequisites are exposed)
# ====================
INCLUDE(CMakePackageConfigHelpers)

# List of targets in this project we want to make visible to the rest of the world.
# They all have to be INSTALL'd with the option "EXPORT ${PROJECT_NAME}TargetGroup"
#SET(_${PROJECT_NAME}_exposed_targets
#)

# Add all targets to the build-tree export set
#EXPORT(TARGETS ${_${PROJECT_NAME}_exposed_targets}
#  FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}Targets.cmake)

# Create the configuration files:
#   - in the build tree:

# Ensure the variables are always defined for the configure:
SET(GUI_ROOT_DIR "${GUI_ROOT_DIR}")

SET(CONF_INCLUDE_DIRS "${PROJECT_SOURCE_DIR}/include" "${PROJECT_BINARY_DIR}/include")

# Build variables that will be expanded when configuring Salome<MODULE>Config.cmake:
# SALOME_CONFIGURE_PREPARE() #For use in the future

CONFIGURE_PACKAGE_CONFIG_FILE(${PROJECT_NAME}Config.cmake.in
    ${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
    INSTALL_DESTINATION "${SALOME_INSTALL_CMAKE_LOCAL}"
    PATH_VARS CONF_INCLUDE_DIRS SALOME_INSTALL_CMAKE_LOCAL CMAKE_INSTALL_PREFIX
    GUI_ROOT_DIR)

WRITE_BASIC_PACKAGE_VERSION_FILE(${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
    VERSION ${${PROJECT_NAME_UC}_VERSION}
    COMPATIBILITY AnyNewerVersion)

# Install the CMake configuration files:
INSTALL(FILES
  "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
  "${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake"
  DESTINATION "${SALOME_INSTALL_CMAKE_LOCAL}")

# Install the export set for use with the install-tree
#INSTALL(EXPORT ${PROJECT_NAME}TargetGroup DESTINATION "${SALOME_INSTALL_CMAKE_LOCAL}"
#  FILE ${PROJECT_NAME}Targets.cmake)

IF(SALOME_BUILD_DOC)
  IF(SALOME_USE_MPI)
    FIND_PACKAGE(SalomeMPI) # needed for doc generation by Sphinx
    SALOME_LOG_OPTIONAL_PACKAGE(MPI SALOME_BUILD_DOC)
  ENDIF()
  FIND_PACKAGE(SalomeDoxygen)
  FIND_PACKAGE(SalomeSphinx)
  SALOME_LOG_OPTIONAL_PACKAGE(Doxygen SALOME_BUILD_DOC)
  SALOME_LOG_OPTIONAL_PACKAGE(Sphinx SALOME_BUILD_DOC)

  ADD_SUBDIRECTORY(doc)

ENDIF()

# Copyright (C) 2009-2025 EDF, OPEN CASCADE
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#

#------------------------------------------------------------

AC_DEFUN([CHECK_CFDSTUDY],[

AC_CHECKING(for CfdStudy)

CfdStudy_ok=no

CFDSTUDY_LDFLAGS=""
CFDSTUDY_CXXFLAGS=""

AC_ARG_WITH(gui,
	    --with-py-light=DIR root directory path of CFDSTUDY installation,
	    CFDSTUDY_DIR="$withval",CFDSTUDY_DIR="")

if test "x$CFDSTUDY_DIR" = "x" ; then

# no --with-light option used

  if test "x$CFDSTUDY_ROOT_DIR" != "x" ; then

    # CFDSTUDY_ROOT_DIR environment variable defined
    LIGHT_DIR=$CFDSTUDY_ROOT_DIR

  else

    # search CFDSTUDY binaries in PATH variable
    AC_PATH_PROG(TEMP, CFDSTUDYGUI.py)
    if test "x$TEMP" != "x" ; then
      CFDSTUDY_BIN_DIR=`dirname $TEMP`
      CFDSTUDY_DIR=`dirname $CFDSTUDY_BIN_DIR`
    fi

  fi
#
fi

if test -f ${CFDSTUDY_DIR}/lib/salome/CFDSTUDYGUI.py  ; then
  CfdStudy_ok=yes
  AC_MSG_RESULT(Using CFDSTUDY distribution in ${CFDSTUDY_DIR})

  if test "x$CFDSTUDY_ROOT_DIR" == "x" ; then
    CFDSTUDY_ROOT_DIR=${CFDSTUDY_DIR}
  fi
  AC_SUBST(CFDSTUDY_ROOT_DIR)
else
  AC_MSG_WARN("Cannot find compiled CFDSTUDY distribution")
fi

AC_MSG_RESULT(for CFDSTUDY: $CfdStudy_ok)

])dnl


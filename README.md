General Information
===================

This directory contains the salome_cfd extensions for the
code_saturne (https://code-saturne.org) CFD tool,
EDF's general purpose Computational Fluid Dynamics (CFD) software.

These extension provide better integration with the SALOME plarform
(https://www.salome-platform.org).

Presentation
============

The salome_cfd extensions provide increased integration of code_saturne
in the Salome platform, especially:

* the CFD_STUDY module for integration of the code_saturne GUI in the SALOME
  workbench; this also allows visualization of probe positions and boundary
  groups relative to the mesh;

* integration with OpenTURNS and the PERSALYS graphical interface for
  sensitivity studies.

Copying
=======

The salome_cfd extensions for code_saturne are distributed under the GNU
General Public Licence, v2. or higher. See the COPYING file for details.

Installation
============

Installation can be done indepedently of that of code_saturne, as only
executing the installed modules requires than an actual build is present.
It is usually done as a post-install step.

It is based on GNU autotools, so the classical
`configure && make && make install` paradigm may be used here.
It is strongly recommended to build ouside the source tree (i.e. run
`configure` from outside the source tree, in a dedicated build directory),
and in-tree builds are not supported.

The path of a matching installation of code_saturne should be
specified using the `CS_ROOT_DIR` variable, either
specified when running `configure`, or defined as an environement
variable at runtime. If both methods are used, the environment
variable has priority over the initial configuratio setting.

The matching code_saturne installation may use different versions of some
optional libraries, though using the same ones is usually recommended,
and at least Python and PyQt versions must match.

To obtain available options, run `configure --help`

Code_Saturne support: saturne-support@edf.fr

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

To list available options, run `configure --help`

The path of a matching installation of code_saturne should be
specified using the `CS_ROOT_DIR` variable, either
specified when running `configure`, or defined as an environement
variable at runtime. If both methods are used, the environment
variable has priority over the initial configuratio setting.

The associated code_saturne installation may use different versions of some
optional libraries, though using the same ones is usually recommended,
and at least Python and PyQt versions must match.

PyQt5 is used by SALOME versions 8 and above, while PyQt4 was used for
older versions. Using code_saturne with SALOME versions older than
9.3 might work, but is not supported.

Required code_saturne build structure
-------------------------------------

SALOME expects a specific directory tree when loading modules,
so CFDSTUDY may be ignored when installing with a specified (i.e. non-default)
`--datarootdir` path in the `configure` options.

Environment modules
--------------------

Some SALOME builds may require loading of environment modules to handle
some prerequisites. The `<install-prefix>/bin/salome_cfd` command should load
those automatically once installed, but for the configuration and make
stages, modules should be loaded manually. To make this easier,
the following command may be used (replacing `<top_source_dir>`
and `<salome_root_directory>` with the actual directory names:

```
$ for m in `<top_source_dir>/build-aux/list_salome_modules.py <salome_root_directory>`;
do
 module load $m;
done
```

known issues
------------

With some builds from the
[http://www.salome-platform.org](http://www.salome-platform.org)
downloads, building CFDSTUDY may fail due to the `omniidl` script containing
non-existent paths. In this case, add:

`OMNIIDL=<salome_root_directory>/INSTALL/omniORB/bin/omniidl`

to the salome_cfd_extensions `configure` options to work around this issue.

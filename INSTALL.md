<!--
  This file is part of code_saturne, a general-purpose CFD tool.

  Copyright (C) 1998-2024 EDF S.A.

  This program is free software; you can redistribute it and/or modify it under
  the terms of the GNU General Public License as published by the Free Software
  Foundation; either version 2 of the License, or (at your option) any later
  version.

  This program is distributed in the hope that it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
  details.

  You should have received a copy of the GNU General Public License along with
  this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
  Street, Fifth Floor, Boston, MA 02110-1301, USA.
-->

salome_cfd extensions installation documentation
================================================

Installation can be done independently of that of code_saturne, as only
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
variable has priority over the initial configuration setting.

The associated code_saturne installation may use different versions of some
optional libraries, though using the same ones is usually recommended,
and at least Python and PyQt (PyQt5) versions must match.

Installation directory structure
--------------------------------

Installation of these extensions assume 3 separate parts:
- An existing SALOME installation, in a directory hereafter referenced as
  `salome_root_dir`.
- An existing code_saturne installation, in a directory referenced by the
  `CS_ROOT_DIR` directory.
  * In complete salome_cfd_distributions, the directory will usually be
    found at `${salome_root_dir}/EDF/s-saturne`, but there is no requirement
    that it be placed inside the SALOME directory tree, so a user may use
    an existing (and separate) code_saturne build.
- The salome_cfd extensions with be installed in the path specified by
  the `--prefix` configure option.
  * In complete salome_cfd_distributions, the directory will usually be
    found at `${salome_root_dir}/EDF/s-cfd-study`, but there is no requirement
    that it be placed there or even inside the SALOME directory tree, so a user
    may choose another path if desired.

The installed salome_cfd_extensions will only be usable from SALOME if
the required environment information is provided.
- When specifying an integer id with the `--with-env-id=<id>` configure option,
  the salome_cfd_extension installation will configure install 2 files
  in the SALOME installation:
  * `${salome_root_dir}.extra.env.d/<id>_s_cfd_study.py`
  * `${salome_root_dir}.extra.env.d/<id>_s_cfd_study.sh`

  It is recommended to use an id higher than those of other files present
  in the `extra.env.d` directory, as the files will be loaded in order of
  increasing id.

- If no id is specified, the user will need to provide this information
  by defining similar files. In reference salome_cfd distributons, this is
  handled by the installer's build system, which generates a series of
  `.py` and `.sh` files under `${salome_root_dir}.extra.env.d`
  (for example `017_s_saturne.*`, `019_s_cfd_study.*`, ...)

For a user-defined installation, letting the salome_cfd_extensions create
these files automatically, for example adding `--with-env-id=120` to the
`configure` options is recommended.

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

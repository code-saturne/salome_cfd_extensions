## Process this file with automake to produce Makefile.in

#-------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2024 EDF S.A.
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

#-------------------------------------------------------------------------------

if HAVE_SPHINX
SPHINX_SUBDIRS = doc
endif

SUBDIRS = idl resources src $(SPHINX_SUBDIRS)

EXTRA_DIST = \
$(AUX_DIST) \
env/cfd_study.py.in \
env/cfd_study.sh.in

DISTCLEANFILES = \
env/cfd_study.py \
env/cfd_study.sh

# Replace paths in Python scripts.
# The following command and target is adapted from an example in
# autoconf. The autoconf documentation recommends changing scripts
# through Makefile targets rather than through configure, and
# cites its own automate and autoheader as examples.

edit_package = sed \
	-e 's|@python_version[@]|$(PYTHON_VERSION)|g' \
	-e 's|@prefix[@]|$(prefix)|g' \
	-e 's|@cs_root_dir[@]|$(CS_ROOT_DIR)|g'

# Environment files

local_env_files = env/cfd_study.py env/cfd_study.sh

env/cfd_study.py: Makefile $(srcdir)/env/cfd_study.py.in
	rm -f $@ $@.tmp
	$(MKDIR_P) env
	srcdir=''; \
	test -f ./$@.in || srcdir=$(srcdir)/; \
	$(edit_package) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

env/cfd_study.sh: Makefile $(srcdir)/env/cfd_study.sh.in
	rm -f $@ $@.tmp
	$(MKDIR_P) env
	srcdir=''; \
	test -f ./$@.in || srcdir=$(srcdir)/; \
	$(edit_package) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

clean-local:
	@list=; for p in ${local_env_files}; do \
	  if test -f $$p; then \
	    echo "rm -f $$p"; \
	    rm -f $$p; \
	  else :; fi; \
	done
	-rm -rf env

all-local: ${local_env_files}

install-exec-local: ${local_env_files}
	@if test "x$(cfd_study_env_id)" != "x"; then \
	  if test -d "$(salome_root_dir)/extra.env.d"; then \
	    echo "in all local $(cfd_study_env_id)"; \
	    for p in ${local_env_files}; do \
	      pb=`basename $$p` ; \
	      echo " cp -fp $$p ${salome_root_dir}/extra.env.d/$(cfd_study_env_id)_s_$$pb"; \
	      cp -fp $$p "${salome_root_dir}/extra.env.d/$(cfd_study_env_id)_s_$$pb"; \
	    done; \
	  fi \
	fi

uninstall-local:
	@if test "x$cfd_study_env_id" != "x"; then \
	  if test -d "$(salome_root_dir)/extra.env.d"; then \
	    echo "in all local $(cfd_study_env_id)"; \
	    for p in ${local_env_files}; do \
	      pb=`basename $$p` ; \
	      echo " rm -f $$p ${salome_root_dir}/extra.env.d/$(cfd_study_env_id)_s_$$pb"; \
	      rm -f $$p "${salome_root_dir}/extra.env.d/$(cfd_study_env_id)_s_$$pb"; \
	    done; \
	  fi \
	fi

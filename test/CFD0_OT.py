# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2026 EDF S.A.
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


def _exec(X0):
    from cfdstudy.CFDSTUDYOTURNS_StudyInterface import cfd_openturns_study

    Temp_IN = X0

    cfd_eval = cfd_openturns_study(study_path = {study_path!r},
                                    study_cfg  = {ot_config!r},
                                    vars_dico  = {{"Temp_IN":Temp_IN}})
    cfd_eval.study2code()

    cfd_eval.run()

    (Y0,) = cfd_eval.code2study(n_values=1)

    return Y0


# Copyright (C) 2020 Andrew Trettel
#
# This file is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This file is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this file.  If not, see <https://www.gnu.org/licenses/>.

project=sheardata

database=$(project).db

study_targets := $(filter-out create_tables.tmp sheardata.tmp,$(patsubst %.py,%.tmp,$(wildcard *.py)))

$(database): $(project).tmp $(study_targets)

$(project).tmp: create_tables.py
	PYTHONPATH=$(PYTHONPATH):`pwd` python3 -B $^ $(database)
	@touch $@

%.tmp:: %.py $(project).tmp
	PYTHONPATH=$(PYTHONPATH):`pwd` python3 -B $< $(database)
	@touch $@

.PHONY: clean
clean:
	-rm -fv $(database)
	-rm -fv *.tmp

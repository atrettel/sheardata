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

latex_compiler=pdflatex
bib_compiler=biber

database=$(project).db

preprocessing_targets := $(filter-out ,$(patsubst %.py,%.tmp,$(wildcard pre_*.py)))
postprocessing_targets := $(filter-out ,$(patsubst %.py,%.tmp,$(wildcard post_*.py)))

tex_dependencies = $(project).tex $(wildcard ../data/*.tex) $(postprocessing_targets) figure-tree-diagram.tex.tmp $(project).bcf

$(database): $(project).tmp $(preprocessing_targets)

$(project).tmp: create_tables.py
	PYTHONPATH=$(PYTHONPATH):`pwd` python3 -B $^ $(database)
	@touch $@

pre_%.tmp:: pre_%.py $(project).tmp
	PYTHONPATH=$(PYTHONPATH):`pwd` python3 -B $< $(database)
	@touch $@

post_%.tmp:: post_%.py $(database)
	PYTHONPATH=$(PYTHONPATH):`pwd` python3 -B $< $(database)
	-sed -i "s/\\\\sffamily\\\\fontsize{.*}{.*}\\\\selectfont //g" *.pgf
	-sed -i "s/use as bounding box, clip/use as bounding box/g" *.pgf
	@touch $@

figure-tree-diagram.tex.tmp: $(postprocessing_targets)
	dot2tex figure-tree-diagram.gv --output $@ --usepdflatex --figonly
	sed -i "s/article/standalone/g" $@
	sed -i "/enlarge/d" $@

$(project).pdf: $(tex_dependencies)
	$(latex_compiler) $<
	$(latex_compiler) $<

$(project).bcf: $(project).bib
	$(latex_compiler) $(project).tex
	$(bib_compiler) $(project)
	$(latex_compiler) $(project).tex
	$(bib_compiler) $(project)
	$(latex_compiler) $(project).tex

$(project).bib: ../data/references.bib
	cp -v $^ $@

.PHONY: clean
clean:
	-rm -fv $(database)
	-rm -fv *-blx.bib
	-rm -fv *.aux
	-rm -fv *.bak
	-rm -fv *.bbl
	-rm -fv *.bcf
	-rm -fv *.bib
	-rm -fv *.blg
	-rm -fv *.end
	-rm -fv *.gv
	-rm -fv *.lof
	-rm -fv *.log
	-rm -fv *.lot
	-rm -fv *.out
	-rm -fv *.pdf
	-rm -fv *.pgf
	-rm -fv *.run.xml
	-rm -fv *.tmp
	-rm -fv *.toc
	-rm -fv *.xwm

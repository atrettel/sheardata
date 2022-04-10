# Copyright (C) 2020-2021 Andrew Trettel
#
# SPDX-License-Identifier: MIT

project=sheardata

latex_compiler=pdflatex
bib_compiler=biber

database=$(project).db

preprocessing_targets := $(filter-out ,$(patsubst %.py,%.tmp,$(wildcard pre_*.py)))
postprocessing_targets := $(filter-out ,$(patsubst %.py,%.tmp,$(wildcard post_*.py)))

dot_targets = figure-flow-classification-tree-diagram.tex.tmp
tex_dependencies = $(project).tex $(wildcard ../data/*.tex) $(postprocessing_targets) $(dot_targets) $(project).bcf

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

figure-%-tree-diagram.tex.tmp: $(postprocessing_targets)
	dot2tex figure-$*-tree-diagram.gv --output $@ --usepdflatex --figonly
	sed -i "s/article/standalone/g" $@
	sed -i "/enlarge/d" $@

$(project).tex: ../data/main.tex
	cp -v $< $@

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
	-rm -fv $(project).tex
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

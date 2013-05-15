# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
BUILDDIR      = xde_spacemouse-doc

# Internal variables.
ALLSPHINXOPTS   = $(SPHINXOPTS) doc

.PHONY: help clean doc

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  doc       to make standalone HTML files"
	@echo "  clean     to clean"

clean:
	-rm -rf $(BUILDDIR)/*

doc:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)."


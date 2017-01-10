# Copyright 2017 6WIND S.A.

DOC_TOOLS ?= /foo/bar

DOC_VERSION = $(shell git describe --always | sed 's/supervision-grafana-v//')

NAME = 6wind-app-note-supervision-grafana
PDF_NAME = $(NAME)
ARCHIVE = $O/$(NAME)-v$(DOC_VERSION).tgz

override DESTDIR = $O/$(NAME)

include $(DOC_TOOLS)/doc-tools.mk

CLEAN_DIRS += "$(DESTDIR)" "$(ARCHIVE)"

archive: html-install pdf-install
	@echo '  GEN $(ARCHIVE)'
	$Q tar -zcf $(ARCHIVE) $(DESTDIR) --transform 's,$O/,,'

INSTALL_URL = dst_dir/

install: html-install pdf-install
	@echo '  INSTALL to $(INSTALL_URL)'
	$Q rsync -av --delete $(DESTDIR)/ $(INSTALL_URL)/supervision-grafana/

.PHONY: archive install

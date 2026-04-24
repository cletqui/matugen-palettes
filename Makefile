PALETTE_DIR := $(HOME)/.config/matugen/palettes
PALETTES    := $(wildcard *.json)

.PHONY: install uninstall check help

help:
	@echo "Targets:"
	@echo "  install    Symlink all palettes to $(PALETTE_DIR)"
	@echo "  uninstall  Remove symlinks from $(PALETTE_DIR)"
	@echo "  check      Run the validation script against all palettes"

install:
	@mkdir -p "$(PALETTE_DIR)"
	@for f in $(PALETTES); do \
		ln -sf "$(CURDIR)/$$f" "$(PALETTE_DIR)/$$f" && echo "  linked $$f"; \
	done
	@echo "Done. $(words $(PALETTES)) palette(s) installed."
	@echo "Note: rofi/bin/wallpaper.sh uses 'find -L' to follow these symlinks."

uninstall:
	@for f in $(PALETTES); do \
		rm -f "$(PALETTE_DIR)/$$f" && echo "  removed $$f"; \
	done
	@echo "Done."

check:
	@python3 validate.py $(PALETTES)

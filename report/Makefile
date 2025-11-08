# Makefile for LaTeX report compilation

# Main document
MAIN = main
OUTPUT = ADA_report_OSM_TSP

# LaTeX compiler
LATEX = pdflatex
BIBTEX = bibtex

# Flags
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error

.PHONY: all clean cleanall view

# Default target
all: $(OUTPUT).pdf

# Compile LaTeX document
$(OUTPUT).pdf: $(MAIN).tex
	@echo "Compiling LaTeX document..."
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Running second pass..."
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@mv $(MAIN).pdf $(OUTPUT).pdf
	@echo "PDF generated: $(OUTPUT).pdf"

# Compile with bibliography
full: $(MAIN).tex
	@echo "Full compilation with bibliography..."
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	$(BIBTEX) $(MAIN)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@mv $(MAIN).pdf $(OUTPUT).pdf
	@echo "PDF generated: $(OUTPUT).pdf"

# Clean auxiliary files
clean:
	@echo "Cleaning auxiliary files..."
	@rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz
	@rm -f *.fdb_latexmk *.fls *.nav *.snm *.vrb
	@echo "Clean complete"

# Clean all generated files including PDF
cleanall: clean
	@echo "Removing PDF..."
	@rm -f $(OUTPUT).pdf $(MAIN).pdf
	@echo "All clean"

# View the PDF (Linux/macOS)
view: $(OUTPUT).pdf
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(OUTPUT).pdf; \
	elif command -v open > /dev/null; then \
		open $(OUTPUT).pdf; \
	else \
		echo "Please open $(OUTPUT).pdf manually"; \
	fi

# Help
help:
	@echo "LaTeX Report Makefile"
	@echo "====================="
	@echo ""
	@echo "Targets:"
	@echo "  make          - Compile the PDF (default)"
	@echo "  make full     - Compile with bibliography"
	@echo "  make clean    - Remove auxiliary files"
	@echo "  make cleanall - Remove all generated files"
	@echo "  make view     - Open the PDF"
	@echo "  make help     - Show this help message"


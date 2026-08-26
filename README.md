# Incomprehensible Ex
Sublime Text plugin to read or edit incomprehensible extensions as docx, odt, pdf, epub and more.

---

About

    Recognized extensions in read mode:
        csv, doc, docx, eml, epub, gif, jpg, json, html, mp3, msg, odt, ogg, pdf, png, pptx, ps, rtf,
        tiff, txt, wav, xlsx, xls

    Extensions available in edit mode:
        asciidoc, beamer, commonmark, context, docbook, docx, dokuwiki, dzslides, fb2, haddock, html,
        html5, icml, latex, man, markdown, markdown_github, markdown_mmd, markdown_phpextra,
        markdown_strict, mediawiki, native, odt, opendocument, opml, org, plain, revealjs, rst, rtf, s5,
        slideous, slidy, texinfo, textile

Configuration

    In the configuration you can configure the extensions that will be recognized by the plugin in read mode.
    To configure the extensions do:
        1 - Use command (Ctrl+Shift+p) and type 'Incomprehensible' or 'edit mode'.
        2 - Choose the option "Incomprehensible Ex: Manage Settings".
        3 - Configure the extensions in the file.

    You can choose which extraction engine is used in read mode.
    Supported general engines:
        - docling (default)
        - markitdown
        - pandoc
        - anydoc
        - eml2md

    Supported extension-specific engines (for faster, focused extraction):
        - pymupdf (for PDF)
        - pdfly (for PDF)
        - python-docx (for DOCX)
        - python-pptx (for PPTX)
        - openpyxl (for XLSX)

    You can map specific engines to specific file extensions in the settings. If a conversion fails entirely, the plugin will safely fallback to displaying the raw file bytes using Sublime Text's default binary handling.

    You can set a default operating mode.
    To configure the mode do:
        1 - Use command (Ctrl+Shift+p) and type 'Incomprehensible' or 'edit mode'.
        2 - Choose the option "Incomprehensible Ex: Manage Settings".
        3 - Configure the default mode in the file.

Installation

    [OPTION 1: PACKAGE CONTROL]
    The easiest way to install this plugin is with Package Control.
        1 - Open the command palette with Ctrl+Shift+P.
        2 - Run "Package Control: Install Package".
        3 - Search for "Incomprehensible Ex".
        4 - Install the package and restart Sublime Text if needed.

    [OPTION 2: MANUAL INSTALL]
    If you want to install this repository directly:
        1 - Open your Sublime Text "Packages" directory.
        2 - Clone this repository into that folder.
        3 - Keep the package folder name as "Incomprehensible Ex".

    Example manual install:
        git clone -b develop https://github.com/yuxiaoli/Incomprehensible-ex.git "Incomprehensible Ex"

    [SYSTEM DEPENDENCIES]
    This package uses external tools depending on which engine you choose.

    Read mode engines:
        - docling (default): install docling into a system Python that Sublime can reach.
        - markitdown: install markitdown into a system Python that Sublime can reach.
        - anydoc: install firecrawl-anydoc into a system Python that Sublime can reach.
        - pandoc: install pandoc in your system PATH.
        - extension-specific: install `PyMuPDF` (pymupdf), `pdfly`, `python-docx`, `python-pptx`, or `openpyxl` via pip if using those targeted engines.

    Edit mode saves:
        - pandoc is required to save content back to the original document format.

    Windows example:
        py -3 -m pip install docling
        py -3 -m pip install "markitdown[all]"
        py -3 -m pip install firecrawl-anydoc

    macOS / Linux example:
        python3 -m pip install --user docling
        python3 -m pip install --user "markitdown[all]"
        python3 -m pip install --user firecrawl-anydoc

    Pandoc:
        - Install pandoc from http://pandoc.org/installing.html

    [VERIFY THE INSTALLATION]
    After installing dependencies, verify them from a terminal.

    Windows example:
        py -3 -c "import docling; print('docling ok')"
        py -3 -c "import markitdown; print('markitdown ok')"
        py -3 -c "import anydoc; print('anydoc ok')"
        pandoc --version
        eml2md --version

    macOS / Linux example:
        python3 -c "import docling; print('docling ok')"
        python3 -c "import markitdown; print('markitdown ok')"
        python3 -c "import anydoc; print('anydoc ok')"
        pandoc --version
        eml2md --version

    If Sublime Text still cannot find the tools:
        - Restart Sublime Text after installing Python packages or pandoc.
        - Start Sublime Text from a terminal so it inherits your PATH.
        - Make sure the same system Python you used for installation is the one available as `py`, `python`, or `python3`.

    [SETTINGS AFTER INSTALL]
    After the package is installed:
        1 - Open the command palette with Ctrl+Shift+P and run "Incomprehensible Ex: Manage Settings".
        2 - Or open Preferences -> Package Settings -> Incomprehensible Ex -> Manage Settings.
        3 - Configure the `engines`, `extensions`, and `edit_mode` settings as needed.

    Example settings:
        {
            "engines": {
                "default": "docling",
                "pdf": "pymupdf",
                "docx": "python-docx"
            },
            "edit_mode": false
        }

Usage

    Just open a file with the desired extension, as long as it is configured in the plugin settings file,
    a new unsaved view with the proper extension (e.g., .md or .txt) will open.

    [EDIT MODE] [!WARNING!]
        In edit mode, if you save the document (Ctrl+S), it will overwrite the original binary file. You will lose the styles and formatting of the document because of file conversion.

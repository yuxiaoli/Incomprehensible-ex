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
    Supported engines:
        - docling (default)
        - markitdown
        - pandoc

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
        - pandoc: install pandoc in your system PATH.

    Edit mode saves:
        - pandoc is required to save `.inex` content back to the original document format.

    Windows example:
        py -3 -m pip install docling
        py -3 -m pip install "markitdown[all]"

    macOS / Linux example:
        python3 -m pip install --user docling
        python3 -m pip install --user "markitdown[all]"

    Pandoc:
        - Install pandoc from http://pandoc.org/installing.html

    [VERIFY THE INSTALLATION]
    After installing dependencies, verify them from a terminal.

    Windows example:
        py -3 -c "import docling; print('docling ok')"
        py -3 -c "import markitdown; print('markitdown ok')"
        pandoc --version

    macOS / Linux example:
        python3 -c "import docling; print('docling ok')"
        python3 -c "import markitdown; print('markitdown ok')"
        pandoc --version

    If Sublime Text still cannot find the tools:
        - Restart Sublime Text after installing Python packages or pandoc.
        - Start Sublime Text from a terminal so it inherits your PATH.
        - Make sure the same system Python you used for installation is the one available as `py`, `python`, or `python3`.

    [SETTINGS AFTER INSTALL]
    After the package is installed:
        1 - Open the command palette with Ctrl+Shift+P and run "Incomprehensible Ex: Manage Settings".
        2 - Or open Preferences -> Package Settings -> Incomprehensible Ex -> Manage Settings.
        3 - Configure the `engine`, `extensions`, and `edit_mode` settings as needed.

    Example settings:
        {
            "engine": "docling",
            "edit_mode": false
        }

Usage

    Just open a file with the desired extension, as long as it is configured in the plugin settings file,
    a new file with the extension [.inex] will open.

    [EDIT MODE] [!WARNING!]
        In edit mode, if you save a document you will lose the styles and formatting of the document because
        of file conversion.

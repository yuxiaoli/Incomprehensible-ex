import os
import re
import subprocess
import sublime
import sublime_plugin
import threading


SETTINGS_FILENAME = "incomprehensibleex.sublime-settings"
SETTINGS_CHANGE_KEY = "incomprehensible_ex"
ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

DOCLING_SCRIPT = """
from pathlib import Path
import sys
from docling.document_converter import DocumentConverter

input_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
result = DocumentConverter().convert(input_path)
document = getattr(result, "document", None)
if document is None:
    raise SystemExit("Docling conversion failed: no document produced")
content = document.export_to_text()
if not content.endswith("\\n"):
    content += "\\n"
output_path.write_text(content, encoding="utf-8")
"""

MARKITDOWN_SCRIPT = """
from pathlib import Path
import sys
from markitdown import MarkItDown

input_path = sys.argv[1]
output_path = Path(sys.argv[2])
result = MarkItDown().convert(input_path)
content = getattr(result, "text_content", None)
if not content:
    raise SystemExit("MarkItDown conversion failed: no content produced")
if not content.endswith("\\n"):
    content += "\\n"
output_path.write_text(content, encoding="utf-8")
"""


def plugin_loaded():
    IncomprehensibleEx.ensure_settings_loaded()
    if IncomprehensibleEx.fileSettings is not None:
        IncomprehensibleEx.fileSettings.clear_on_change(SETTINGS_CHANGE_KEY)
        IncomprehensibleEx.fileSettings.add_on_change(
            SETTINGS_CHANGE_KEY, IncomprehensibleEx.ensure_settings_loaded
        )


def plugin_unloaded():
    if IncomprehensibleEx.fileSettings is not None:
        IncomprehensibleEx.fileSettings.clear_on_change(SETTINGS_CHANGE_KEY)


class IncomprehensibleEx(sublime_plugin.EventListener):

    print("** Incomprehensible Extensions Started **")

    DEFAULT_EXTENSIONS = [
        "mp3", "odt", "ogg", "pdf", "pptx", "ps", "psv", "rtf", "tff", "tif",
        "tiff", "tsv", "wav", "xls", "xlsx", "doc", "docx", "eml", "epub"
    ]
    EDITABLE_EXTENSIONS = [
        "asciidoc", "beamer", "commonmark", "context", "docbook", "docx",
        "dokuwiki", "dzslides", "fb2", "haddock", "html", "html5", "icml",
        "latex", "man", "markdown", "markdown_github", "markdown_mmd",
        "markdown_phpextra", "markdown_strict", "mediawiki", "native", "odt",
        "opendocument", "opml", "org", "plain", "revealjs", "rst", "rtf", "s5",
        "slideous", "slidy", "texinfo", "textile"
    ]
    SUPPORTED_ENGINES = ("docling", "markitdown", "pandoc")
    DEFAULT_ENGINE = "docling"

    extensions = list(DEFAULT_EXTENSIONS)
    editable_extensions = list(EDITABLE_EXTENSIONS)
    editMode = False
    engine = DEFAULT_ENGINE
    fileSettings = None
    thread = None

    @classmethod
    def ensure_settings_loaded(cls):
        settings = sublime.load_settings(SETTINGS_FILENAME)
        changed = False

        if not settings.has("extensions"):
            settings.set("extensions", list(cls.DEFAULT_EXTENSIONS))
            changed = True
        if not settings.has("edit_mode"):
            settings.set("edit_mode", cls.editMode)
            changed = True
        if not settings.has("engine"):
            settings.set("engine", cls.DEFAULT_ENGINE)
            changed = True

        raw_extensions = settings.get("extensions", list(cls.DEFAULT_EXTENSIONS))
        if not isinstance(raw_extensions, list):
            raw_extensions = list(cls.DEFAULT_EXTENSIONS)
            settings.set("extensions", raw_extensions)
            changed = True

        normalized_extensions = []
        for item in raw_extensions:
            if isinstance(item, str) and item.strip():
                normalized_extensions.append(item.strip().lower())

        if not normalized_extensions:
            normalized_extensions = list(cls.DEFAULT_EXTENSIONS)
            settings.set("extensions", normalized_extensions)
            changed = True

        cls.extensions = normalized_extensions
        cls.editMode = bool(settings.get("edit_mode", False))

        engine = settings.get("engine", cls.DEFAULT_ENGINE)
        if not isinstance(engine, str):
            engine = cls.DEFAULT_ENGINE
        engine = engine.strip().lower()
        if engine not in cls.SUPPORTED_ENGINES:
            print(
                "Incomprehensible Ex | Unsupported engine '{0}', falling back to '{1}'".format(
                    engine, cls.DEFAULT_ENGINE
                )
            )
            engine = cls.DEFAULT_ENGINE
            changed = True

        if settings.get("engine") != engine:
            settings.set("engine", engine)
            changed = True

        cls.engine = engine
        cls.fileSettings = settings

        if changed:
            sublime.save_settings(SETTINGS_FILENAME)

    def on_load(self, view):
        try:
            type(self).ensure_settings_loaded()
            file_info = self.get_file_info(view)
            if file_info is None:
                return

            path, file_name, extension = file_info
            if extension not in type(self).extensions:
                return

            window = view.window() or sublime.active_window()
            if window is not None:
                window.run_command("close")

            inp = os.path.join(path, file_name)
            out = inp + ".inex"
            self.thread = threading.Thread(
                target=self.handle_active,
                args=(view, inp, out, extension),
                name=file_name
            )
            self.thread.start()
        except Exception as error:
            print("Incomprehensible Ex on_load error:", error)

    def on_pre_close(self, view):
        try:
            if not view.is_scratch() and self.get_view_extension(view) == "inex":
                self.deleteTemp(view)
        except Exception:
            return

    def on_post_save(self, view):
        try:
            if not view.is_scratch() and self.get_view_extension(view) == "inex":
                self.saveTemp(view)
        except Exception as error:
            print("Incomprehensible Ex on_post_save error:", error)

    def get_file_info(self, view):
        file_path = view.file_name()
        if not file_path:
            return None

        path, file_name = os.path.split(file_path)
        extension = os.path.splitext(file_name)[1].lstrip(".").lower()
        return path, file_name, extension

    def get_view_extension(self, view):
        file_info = self.get_file_info(view)
        if file_info is None:
            return ""
        return file_info[2]

    def deleteTemp(self, view):
        file_info = self.get_file_info(view)
        if file_info is None:
            return

        temp_path = os.path.join(file_info[0], file_info[1])
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def saveTemp(self, view):
        try:
            type(self).ensure_settings_loaded()
            file_info = self.get_file_info(view)
            if file_info is None:
                return

            path, file_name, _ = file_info
            inp = os.path.join(path, file_name)
            out = os.path.join(path, file_name[:-5])
            ext = os.path.splitext(out)[1].lstrip(".").lower()

            if ext in type(self).editable_extensions and type(self).editMode:
                self.convert(inp, out, ext, True)
            else:
                print(
                    "[{0}] is not supported for edit mode or cannot be saved back.".format(
                        ext
                    )
                )
        except Exception as error:
            print("Incomprehensible Ex saveTemp error:", error)

    def get_python_launchers(self):
        if os.name == "nt":
            return [
                ["py", "-3"],
                ["py"],
                ["python"],
                ["python3"],
                ["py", "-3.11"],
                ["py", "-3.12"],
            ]
        return [["python3"], ["python"]]

    def build_command_specs(self, inp, temp_out, ext, save):
        if save:
            return [
                {
                    "command": ["pandoc", "-s", "-o", temp_out, "-w", ext, inp],
                    "label": "pandoc",
                }
            ]

        engine = type(self).engine
        if engine == "pandoc":
            return [
                {
                    "command": ["pandoc", "-s", "-t", "plain", "-o", temp_out, inp],
                    "label": "pandoc",
                }
            ]
        if engine == "docling":
            return [
                {
                    "command": launcher + ["-c", DOCLING_SCRIPT, inp, temp_out],
                    "label": "docling ({0})".format(" ".join(launcher)),
                }
                for launcher in self.get_python_launchers()
            ]
        if engine == "markitdown":
            return [
                {
                    "command": launcher + ["-c", MARKITDOWN_SCRIPT, inp, temp_out],
                    "label": "markitdown ({0})".format(" ".join(launcher)),
                }
                for launcher in self.get_python_launchers()
            ]
        raise ValueError("Unsupported engine: {0}".format(engine))

    def run_command_specs(self, command_specs):
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        last_result = None
        retryable_error_markers = (
            "No module named",
            "ModuleNotFoundError",
            "ImportError",
            "No suitable Python runtime found",
            "Python was not found",
            "Requested Python version",
            "Unable to create process using",
        )

        for command_spec in command_specs:
            try:
                proc = subprocess.Popen(
                    command_spec["command"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False,
                    startupinfo=startupinfo
                )
            except FileNotFoundError as error:
                last_result = {
                    "returncode": 127,
                    "stdout": b"",
                    "stderr": str(error).encode("utf-8", errors="replace"),
                    "label": command_spec["label"],
                }
                continue

            stdout, stderr = proc.communicate()
            result = {
                "returncode": proc.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "label": command_spec["label"],
            }
            last_result = result

            if proc.returncode == 0:
                return result

            error_message = stderr.decode("utf-8", errors="replace")
            if any(marker in error_message for marker in retryable_error_markers):
                continue

            return result

        return last_result

    def convert(self, inp, out, ext, save):
        try:
            temp_out = out + ".tmp"
            if os.path.exists(temp_out):
                os.remove(temp_out)
            if os.path.exists(out) and os.path.getsize(out) == 0:
                os.remove(out)

            command_specs = self.build_command_specs(inp, temp_out, ext, save)
            result = self.run_command_specs(command_specs)
            if result is None:
                raise RuntimeError("No conversion command could be started.")

            if result["returncode"] != 0:
                error_message = (
                    result["stderr"].decode("utf-8", errors="replace").strip()
                    if result["stderr"] else "Unknown error."
                )
                error_message = ANSI_ESCAPE.sub("", error_message)

                if os.path.exists(temp_out):
                    try:
                        os.remove(temp_out)
                    except Exception:
                        pass
                if os.path.exists(out) and os.path.getsize(out) == 0:
                    try:
                        os.remove(out)
                    except Exception:
                        pass

                sublime.error_message(
                    "Incomprehensible Ex conversion failed.\n\n"
                    "Engine: {0}\n"
                    "Command: {1}\n\n"
                    "Details:\n{2}\n\n"
                    "Please check the Sublime console for more details.".format(
                        type(self).engine if not save else "pandoc (save mode)",
                        result["label"],
                        error_message,
                    )
                )
                print("Incomprehensible Ex conversion failed")
                print("Input:", inp)
                print("Output:", out)
                print("Command:", result["label"])
                print("Return code:", result["returncode"])
                if error_message:
                    print(error_message)
                return False

            os.replace(temp_out, out)
            return True

        except Exception as error:
            if "temp_out" in locals() and os.path.exists(temp_out):
                try:
                    os.remove(temp_out)
                except Exception:
                    pass
            print("Incomprehensible Ex exception:", error)
            sublime.error_message(
                "Incomprehensible Ex execution failed.\n\n"
                "Exception: {0}\n\n"
                "Please check the Sublime console for details.".format(error)
            )
            return False

    def handle_active(self, view, inp, out, ext):
        try:
            success = self.convert(inp, out, ext, False)
            if success:
                window = view.window() or sublime.active_window()
                if window is not None:
                    window.open_file(out).run_command(
                        "reindent", {"single_line": False}
                    )
        except KeyError as error:
            print(error)

class IncomprehensibleExEditModeOnCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        try:
            IncomprehensibleEx.ensure_settings_loaded()
            IncomprehensibleEx.editMode = True
            IncomprehensibleEx.fileSettings.set('edit_mode', True)
            sublime.save_settings(SETTINGS_FILENAME)
            sublime.active_window().status_message("Incomprehensible Ex | Edit Mode ON")
        except Exception as e:
            print(e)

class IncomprehensibleExEditModeOffCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        try:
            IncomprehensibleEx.ensure_settings_loaded()
            IncomprehensibleEx.editMode = False
            IncomprehensibleEx.fileSettings.set('edit_mode', False)
            sublime.save_settings(SETTINGS_FILENAME)
            sublime.active_window().status_message("Incomprehensible Ex | Edit Mode OFF")
        except Exception as e:
            print(e)

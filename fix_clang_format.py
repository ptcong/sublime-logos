"""
If you're using CLang Format plugin, this plugin will help you solve problems
while formatting Logos file
"""
import sublime
import sublime_plugin
import re


class FixClangFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        view = self.view

        text = view.substr(sublime.Region(0, view.size()))
        text = re.sub(r"%\s+(hook|end|c|group|orig|hookf|init|ctor|dtor|new|property)(?=[^\w]|$)", "%\\1", text)
        text = re.sub(r"#include", "#import", text)

        # fix function pointer
        text = re.sub(r"\)\r?\n\(", ")(", text)

        newlines = []
        lines = text.split("\n")
        countline = len(lines)
        index = 0
        for i in range(0, countline):
            line = lines[i]
            match = (re.match(r"^\s+(@(?:interface|implementation).*$)", line)
                     or re.match(r"^\s+([-+]\s*\([a-zA-Z_][a-zA-Z0-9_\s]+\s*\*?\s*\).*$)", line)
                     or re.match(r"^\s+(%(?:hook|hookf|group|ctor|dtor|new|end).*$)", line))
            if match != None:
                line = match.group(1)

            if re.match(r"^([-+]\s*\([a-zA-Z_][a-zA-Z0-9_\s]+\s*\*?\).*$)", line):
                line = re.sub(r"([a-zA-Z0-9_]+)\s+:\s*", "\\1:", line)
                for j in range(index, min(countline, index + 10)):
                    if re.match(r"^\s*\{", lines[j]) or lines[j].endswith(";"):
                        break
                    lines[j] = re.sub(r"([a-zA-Z0-9_]+)\s+:\s*", "\\1:", lines[j])

            if re.match(r"^%(end|group)", lines[index]):
                if re.match(r"^%end", lines[index]) and lines[index] != r"%end":
                    newlines.append(r"%end")
                    line = lines[index] = re.sub(r"^%end\s*", "", lines[index])

                for j in range(index + 1, countline):
                    if re.match(r"^\s+[a-zA-Z_]", lines[j]):
                        if lines[j].strip()[-1] != ";":
                            lines[j + 1] = lines[j].strip() + " " + lines[j + 1].lstrip()
                            lines[j] = ""
                        else:
                            lines[j] = lines[j].lstrip()
                    if lines[j].strip() != "":
                        break

            newlines.append(line)
            index += 1

        view.replace(edit, sublime.Region(0, view.size()), "\n".join(newlines))


class EventListener(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        if view.file_name().endswith((".xm")):
            view.run_command("fix_clang_format")

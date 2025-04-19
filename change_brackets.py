import sublime
import sublime_plugin

brackets = ("()", "{}", "[]", "''", '""', '``')


class ChangeBracketsCommand(sublime_plugin.TextCommand):
    """Change the quote / brackets around the selection."""

    def run(self, edit):
        if not self.view.sel():
            return

        self.view.window().show_quick_panel(brackets, on_select=self.on_select)
        self.edit = edit

    def on_select(self, option):
        if option < 0:
            return

        self.view.run_command("change_brackets_at", {"bracket": brackets[option]})


class ChangeBracketsAtCommand(sublime_plugin.TextCommand):
    def run(self, edit, bracket):
        if not self.view.sel():
            return

        for sel in list(self.view.sel()):
            a, b = sorted(sel.to_tuple())

            # First try to change the bracket inside the selection
            b1 = sublime.Region(a, a + 1)
            b2 = sublime.Region(b - 1, b)
            br = self.view.substr(b1) + self.view.substr(b2)

            if br in brackets:
                self.view.replace(edit, b1, bracket[0])
                self.view.replace(edit, b2, bracket[1])
                continue

            # Otherwise, look around
            b1 = sublime.Region(a - 1, a)
            b2 = sublime.Region(b, b + 1)
            br = self.view.substr(b1) + self.view.substr(b2)
            if br in brackets:
                self.view.replace(edit, b1, bracket[0])
                self.view.replace(edit, b2, bracket[1])
                continue

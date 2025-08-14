import sublime
import sublime_plugin

brackets = ("()", "{}", "[]", "''", '""', "``")


class ChangeBracketsCommand(sublime_plugin.TextCommand):
    """Change the quote / brackets around the selection."""

    def run(self, edit):
        if not self.view.sel():
            return

        self.regions = _get_regions(self.view)
        if not self.regions:
            return

        self.sel_backup = list(self.view.sel())
        self.view.sel().clear()

        self.view.add_regions(
            "change-brackets-around-sel",
            self.sel_backup,
            icon="",
            scope="comment",
            flags=sublime.DRAW_NO_FILL,
        )
        self.view.add_regions(
            "change-brackets-around-result",
            [r for rr in self.regions for r in rr],
            icon="",
            scope="comment | region.yellowish",
        )

        self.view.window().show_input_panel(
            f"Change brackets: {' '.join(b[0] for b in brackets)}",
            initial_text="",
            on_done=self.on_done,
            on_change=self.on_done,
            on_cancel=self.on_cancel,
        )
        self.edit = edit

    def on_done(self, option):
        bracket = next((b for b in brackets if b[0] in option or b[1] in option), None)
        if bracket is None:
            return
        self.on_cancel()
        self.view.window().run_command("hide_panel", {"cancel": True})
        self.view.run_command(
            "change_brackets_at",
            {
                "bracket": bracket,
                "regions": [(r[0].to_tuple(), r[1].to_tuple()) for r in self.regions],
            },
        )

    def on_cancel(self):
        self.view.erase_regions("change-brackets-around-sel")
        self.view.erase_regions("change-brackets-around-result")
        if not len(self.view.sel()):
            self.view.sel().add_all(self.sel_backup)


class ChangeBracketsAtCommand(sublime_plugin.TextCommand):
    def run(self, edit, bracket, regions):
        for b1, b2 in regions:
            self.view.replace(edit, sublime.Region(*b1), bracket[0])
            self.view.replace(edit, sublime.Region(*b2), bracket[1])


def _get_regions(view):
    regions = []
    for sel in view.sel():
        a, b = sorted(sel.to_tuple())

        # Look around
        b1 = sublime.Region(a - 1, a)
        b2 = sublime.Region(b, b + 1)
        br = view.substr(b1) + view.substr(b2)
        if br in brackets:
            regions.append([b1, b2])
            continue

        # Look inside
        b1 = sublime.Region(a, a + 1)
        b2 = sublime.Region(b - 1, b)
        br = view.substr(b1) + view.substr(b2)

        if br in brackets:
            regions.append([b1, b2])
            continue

    return regions

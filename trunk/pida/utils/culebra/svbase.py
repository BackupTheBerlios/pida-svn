import gtksourceview
from rat import text

class BaseView(gtksourceview.SourceView):
    def __init__(self):
        super(BaseView, self).__init__()
        self.set_auto_indent(True)
        self.set_show_line_numbers(True)
        self.set_show_line_markers(True)
        self.set_tabs_width(4)
        self.set_margin(80)
        self.set_show_margin(True)
        self.set_smart_home_end(True)
        self.set_highlight_current_line(True)
        self.set_insert_spaces_instead_of_tabs(True)
        text.make_source_view_indentable(self)

class BaseBuffer(gtksourceview.SourceBuffer):

    def __init__(self):
        super(BaseBuffer, self).__init__()
        lm = gtksourceview.SourceLanguagesManager()
        language = lm.get_language_from_mime_type("text/x-python")
        self.languages_manager = lm
        self.set_language(language)

        self.set_highlight(True)


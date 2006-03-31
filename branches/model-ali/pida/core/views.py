

class view_mixin(object):

    __views__ = []

    def init(self):
        self.__views = {}
        self.__viewdefs = {}
        for definition in self.__class__.__views__:
            self.__viewdefs[definition.__name__] = definition

    def create_view(self, viewname, **kw):
        viewdef = self.__viewdefs[viewname]
        view = viewdef.view_type(service=self,
                                 prefix=viewname, **kw)
        self.__views[view.unique_id] = view
        view.view_definition = viewdef
        view.connect('removed', self.__view_closed_base)
        return view

    def show_view(self, unique_id=None, view=None):
        if view is None:
            if unique_id is None:
                raise KeyError('Need either view, or unique_id')
            view = self.__views[unique_id]
        book_name = view.view_definition.book_name
        self.boss.call_command('window', 'append_page',
                                bookname=book_name, view=view)

    def raise_view(self, view):
        self.boss.call_command('window', 'raise_page', view=view)

    def get_view(self, unique_id):
        return self.__views[unique_id]

    def get_first_view(self, viewname):
        for view in self.__views.values():
            if view.view_definition.__name__ == viewname:
                return view
        raise KeyError('No views of that type')

    def view_confirm_close(self, view):
        return True

    def view_confirm_detach(self, view):
        return True

    def close_view(self, view):
        if self.view_confirm_close(view):
            self.boss.call_command('window', 'remove_page', view=view)
            view.emit('removed')

    def __view_closed_base(self, view):
        del self.__views[view.unique_id]
        self.view_closed(view)

    def view_closed(self, view):
        pass

    def detach_view(self, view, detach):
        if detach:
            self.boss.call_command('window', 'remove_page', view=view)
            self.boss.call_command('window', 'append_page',
                                   bookname='ext', view=view)
        else:
            self.boss.call_command('window', 'remove_page', view=view)
            self.show_view(view=view)
            

    def view_detached_base(self, view):
        self.view_detached(self, view)

    def view_detached(self, view):
        pass



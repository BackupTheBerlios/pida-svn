





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
        return view

    def show_view(self, unique_id=None, view=None):
        if view is None:
            if unique_id is None:
                raise KeyError('Need either view, or unique_id')
            view = self.__views[unique_id]
        bookname = view.view_definition.bookname
        self.boss.call_command('window', 'add_page',
                               contentview=view,
                               bookname=book_name)

    def hide_view(self, unique_id):
        pass

    def destroy_view(self, unique_id):
        pass

    def get_view(self, unique_id):
        pass

    def get_views(self, viewname):
        pass

    def get_first_view(self, viewname):
        pass

    def view_confirm_close(self, view):
        return True

    def view_confirm_detach(self, view):
        return True

    def view_close(self, view):
        self.boss.call_command('window', 'remove_view',
                               contentview=contentview)

    def view_closed_base(self, view):
        del self.__views[view.unique_id]
        self.view_closed(self, view)

    def view_closed(self, view):
        pass

    def view_detach(self, view):
        pass

    def view_detached_base(self, view):
        self.view_detached(self, view)

    def view_detached(self, view):
        pass

    def cb_view_closed(self, view, viewname):
        pass


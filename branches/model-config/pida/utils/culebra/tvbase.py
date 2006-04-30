import gtk

class BaseBuffer(gtk.TextBuffer):
    def can_undo(self):
        return False
    
    def can_redo(self):
        return False
    
    def begin_not_undoable_action(self):
        pass

    def end_not_undoable_action(self):
        pass

BaseView = gtk.TextView
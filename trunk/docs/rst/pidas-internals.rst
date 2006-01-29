================
PIDA's internals
================

Services:
=============

Service life cycle: init, bind, reset, stop

`init` you cannot rely on the presence of other services. Just your own config.
At `init` you don't even have `action_group`s.

The `bind` is called once all the services have been started.

The `reset` method is called whenever the service must refresh its values. It's
used to refresh the service options and whatnot.

`stop` is called before a service is unloaded.


buffermanager
-------------

Actions it defines:
 - open_file
 - quit_pida
 - new_file
 - save_session
 - load_session

Commands it defines:
 - open_document(document)
 - new_file()
 - open_file(filename)
 - open_file_line(filename, linenumber)
 - close_file(filename)
 - save_session(session_filename)
 - load_session(session_filename)
 - file_closed(filename)
 - reset_current_document()
 
editormanager
-------------

The editormanager is just a proxy to the real editor.

It does not define any action.

Commands it defines:
 - close(filename)
 - revert()
 - start()
 - edit()
 - goto_line()
 - undo()
 - redo()
 - save()
 - cut()
 - copy()
 - paste()
 - can_close(): bool - currently optional see #102

Events it defines:
 - started

documenttypes
-------------

It defines the actions of the toolbar and menubar related to documents.

Actions it defines:
 - redo
 - undo
 - cut
 - copy
 - paste
 - save


Commands it defines: 
 - register_file_handler(handler)
 - create_document(filename, [document_type], **kwargs): document

The handler is a class defined as a variable in the main service and it must
implement the class `pida.core.document.document_handler`. See `gazpach`
service.


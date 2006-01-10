# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com
#Copyright (c) 2006 Bernard Pratz aka Guyzmo, guyzmo@m0g.net

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import pida.core.service as service

defs = service.definitions

import pida.pidagtk.gladeview as gladeview
import pida.pidagtk.progressbar as progressbar
import pida.utils.pastebin

import os
import gtk
import gobject

class paste_editor_view(gladeview.glade_view):
    '''Create and edit a new paste'''

    SHORT_TITLE = 'Create a paste'
    LONG_TITLE = 'Create a paste so you can post it'
    ICON = 'paste'

    # UI loading

    glade_file_name = 'paste-editor.glade'

    def init_glade(self):
        '''Initiate the interface using glade'''
        self.__title_entry = self.get_widget('post_title_entry')
        self.__nickname_entry = self.get_widget('post_name_entry')
        self.__title_entry.set_text('') # TODO: Use options
        self.__nickname_entry.set_text('') # TODO: Use options
        self.__text_entry = self.get_widget('post_text_entry')
        self.__pulse_bar = None
        self.__options = {}
        self.__inputs = {}

    def set_paste_bin(self, pbin):
        '''Sets a pastebin to the view in order to get informations'''
        self.__pastebin = pbin
        self.__pack_combos()
        self.__pack_inputs()

    # private interface

    def __pack_combos(self):
        '''Populate all comboboxes'''
        if self.__pastebin.OPTIONS != None:
            hb = self.get_widget('hb_combos')
            hb.remove(self.get_widget('hseparator_combo'))
            for option in self.__pastebin.OPTIONS.keys():
                label = gtk.Label(option)
                label.show()
                hb.add(label)
                self.__options[option] = gtk.combo_box_new_text()
                for value in self.__pastebin.OPTIONS[option]:
                    self.__options[option].append_text(value)
                self.__options[option].show()
                hb.add(self.__options[option])
    
    def __pack_inputs(self):
        '''Populates all inputs'''
        if self.__pastebin.INPUTS != None:
            vb = self.get_widget('vb_entries')
            for name in self.__pastebin.INPUTS.keys():
                hb = gtk.HBox
                name = gtk.Label(name)
                name.show()
                hb.add(name)
                self.__inputs[name] = gtk.Entry()
                self.__inputs[name].set_text(self.__pastebin.INPUTS[name])
                self.__inputs[name].show()
                hb.add(self.__inputs[name])
                vb.add(hb)

    def __clear(self):
        '''Clears the interface'''
        self.__title_entry.set_text("")
        self.__nickname_entry.set_text("")
        if self.__pastebin.INPUTS != None:
            for name in self.__pastebin.INPUTS.keys():
                self.__inputs[name].set_text("")
        if self.__pastebin.OPTIONS != None:
            for option in self.__pastebin.OPTIONS.keys():
                self.__options[option].set_active(0)
        self.__text_entry.get_buffer().set_text("")

    # public interface

    def pulse(self):
        '''Starts the pulse'''
        if self.__pulse_bar == None:
            hb_pulse = self.get_widget('hb_pulsebar')
            hb_pulse.remove(self.get_widget('hseparator_pulse'))
            self.__pulse_bar = progressbar.progress_bar()
            self.__pulse_bar.set_size_request(-1, 12)
            self.__pulse_bar.set_pulse_step(0.01)
            hb_pulse.add(self.__pulse_bar)
        self.__pulse_bar.show_pulse()

    def close(self):
        '''Stops the pulse'''
        if self.__pulse_bar != None:
            self.__pulse_bar.hide_pulse()
        gladeview.glade_view.close(self)

    # UI callbacks

    def on_post_button__clicked(self,but):
        '''Post the paste'''
        self.__pastebin.set_title(self.__title_entry.get_text())
        self.__pastebin.set_name(self.__nickname_entry.get_text())
        self.__pastebin.set_pass('') ## TODO: USE OPTIONS
        self.__pastebin.set_text(self.__text_entry.get_buffer().get_text(
                    self.__text_entry.get_buffer().get_start_iter(),
                    self.__text_entry.get_buffer().get_end_iter()))
        
        if self.__pastebin.OPTIONS != None:
            options = []
            for option in self.__pastebin.OPTIONS.keys():
                options.append({option:self.__options[option].get_active_text()})
            self.__pastebin.set_options(options)

        if self.__pastebin.INPUTS != None:
            inputs = []
            for name in self.__pastebin.INPUTS.keys():
                inputs.append({name:self.__inputs[name].get_text()})
            self.__pastebin.set_inputs(inputs)
            
        self.__pastebin.set_editor(self)

        but.set_sensitive(False)
        self.service.boss.call_command('pastemanager', 'post_paste', paste=self.__pastebin)

    def on_clear_button__clicked(self,but):
        '''Clears the paste'''
        self.__clear()
        
    def on_close_button__clicked(self,but):
        '''Quits the paste editor without modification'''
        self.close()

class paste_viewer_view(gladeview.glade_view):
    '''View a paste'''

    SHORT_TITLE = 'View a paste'
    LONG_TITLE = 'View a paste'
    ICON = 'paste'

    # UI loading

    glade_file_name = 'paste-viewer.glade'

    def init_glade(self):
        '''Initiate the interface using glade'''
        self.__title_label = self.get_widget('post_title_value')
        self.__nickname_label = self.get_widget('post_nickname_value')
        self.__text_label = self.get_widget('post_text_entry')
    
    def set_paste(self,paste):
        '''Sets a paste to the view in order to get informations'''
        self.__paste = paste
        self.__title_label.set_text(paste.title)
        self.__nickname_label.set_text(paste.name)
        self.__text_label.get_buffer().set_text(paste.text)

        if self.__paste.OPTIONS != None:
            hb = self.get_widget('hb_combos')
            hb.remove(self.get_widget('hseparator_combo'))
            for option in self.__paste.OPTIONS.keys():
                label = gtk.Label(option)
                label.show()
                hb.add(label)
                label = gtk.Label(self.__paste.get_option(option))
                label.show()
                hb.add(label)

        if self.__paste.INPUTS != None:
            vb = self.get_widget('vb_entries')
            for name in self.__paste.INPUTS.keys():
                hb = gtk.HBox
                label = gtk.Label(name)
                label.show()
                hb.add(label)
                label = gtk.Label(self.__paste.get_input(name))
                label.show()
                hb.add(label)
                vb.add(hb)

    def on_open_url_button__clicked(self,but):
        '''Opens the URL of the paste'''
        self.service.boss.call_command('webbrowse','browse',
            url = self.__paste.url, newview = True)
   
    def on_close_button__clicked(self,but):
        '''Quits the paste editor without modification'''
        self.close()


class paste_annotate_view(gladeview.glade_view):
    '''annotate a paste'''

    SHORT_TITLE = 'Annotate a paste'
    LONG_TITLE = 'Annotate a paste'

    # UI loading

    glade_file_name = 'paste-annotate.glade'

    def init_glade(self):
        '''Initiate the interface using glade'''
        self.__post_title_label = self.get_widget('post_title_value')
        self.__nickname_label = self.get_widget('post_nickname_value')
        self.__text_label = self.get_widget('post_text_entry')

        self.__title_entry = self.get_widget('title_annot_entry')
        self.__title_entry.set_text('') # TODO: Use options
        self.__text_entry = self.get_widget('annotation')
        self.__pulse_bar = None
        self.__options = {}
        self.__inputs = {}

    def set_paste_bin(self, pbin):
        '''Sets a paste to the view in order to get informations'''
        self.__pastebin = pbin
        self.__pack_combos()
        self.__pack_inputs()

        self.__post_title_label.set_text(self.__pastebin.title)
        self.__nickname_label.set_text(self.__pastebin.name)
        self.__text_label.get_buffer().set_text(self.__pastebin.text)

        if self.__pastebin.OPTIONS != None:
            hb = self.get_widget('hb_paste_combos')
            hb.remove(self.get_widget('hseparator_paste_combo'))
            for option in self.__pastebin.OPTIONS.keys():
                label = gtk.Label(option)
                label.show()
                hb.add(label)
                hb.add(self.__pastebin.get_option(option))

        if self.__pastebin.INPUTS != None:
            vb = self.get_widget('vb_labels')
            for name in self.__pastebin.INPUTS.keys():
                hb = gtk.HBox
                label = gtk.Label(name)
                label.show()
                hb.add(label)
                hb.add(gtk.Label(self.__pastebin.get_input(name)))
                vb.add(hb)

    # private interface

    def __pack_combos(self):
        if self.__pastebin.OPTIONS != None:
            hb = self.get_widget('hb_combos')
            hb.remove(self.get_widget('hseparator_combo'))
            #TODO annotation's options
            for option in self.__pastebin.OPTIONS.keys():
                label = gtk.Label(option)
                label.show()
                hb.add(label)
                self.__options[option] = gtk.combo_box_new_text()
                for value in self.__pastebin.OPTIONS[option]:
                    self.__options[option].append_text(value)
                self.__options[option].show()
                hb.add(self.__options[option])
    
    def __pack_inputs(self):
        if self.__pastebin.INPUTS != None:
            vb = self.get_widget('vb_entries')
            #TODO annotation's inputs
            for name in self.__pastebin.INPUTS.keys():
                hb = gtk.HBox
                label = gtk.Label(name)
                label.show()
                hb.add(label)
                self.__inputs[name] = gtk.Entry()
                self.__inputs[name].set_text(self.__pastebin.INPUTS[name])
                self.__inputs[name].show()
                hb.add(self.__inputs[name])
                vb.add(hb)

    def __clear(self):
        '''Clears the interface'''
        self.__title_entry.set_text("")
        self.__nickname_entry.set_text("")
        for option, input in __inputs:
            input.set_text("")
        for option, combo in __combos:
            combo.set_active_text(0)
        self.__text_entry.set_text("")

    # public interface

    def pulse(self):
        '''Starts the pulse'''
        if self.__pulse_bar == None:
            hb_pulse = self.get_widget('hb_pulsebar')
            hb_pulse.remove(self.get_widget('hseparator_pulse'))
            self.__pulse_bar = progressbar.progress_bar()
            self.__pulse_bar.set_size_request(-1, 12)
            self.__pulse_bar.set_pulse_step(0.01)
            hb_pulse.add(self.__pulse_bar)
        self.__pulse_bar.show_pulse()

    def close(self):
        '''Stops the pulse'''
        if self.__pulse_bar != None:
            self.__pulse_bar.hide_pulse()
        gladeview.glade_view.close(self)

    # UI callbacks

    def on_post_button__clicked(self,but):
        '''Post the paste'''

        annotation = pastebin.annotation()
        annotation.set_title(self.__title_entry.get_text())
        annotation.set_name(self.__nickname_entry.get_text())
        annotation.set_pass('') ## TODO: USE OPTIONS
        annotation.set_text(self.__text_entry.get_buffer().get_text(
                    self.__text_entry.get_buffer().get_start_iter(),
                    self.__text_entry.get_buffer().get_end_iter()))
        
        #TODO
        if self.__pastebin.OPTIONS != None:
            options = []
            for option in self.__pastebin.OPTIONS.keys():
                options.append({option:self.__options[option].get_active_text()})
            self.__pastebin.set_options(options)

        #TODO
        if self.__pastebin.INPUTS != None:
            inputs = []
            for name in self.__pastebin.INPUTS.keys():
                inputs.append({name:self.__inputs[name].get_text()})
            self.__pastebin.set_inputs(inputs)
            
        self.__pastebin.set_editor(self)

        but.set_sensitive(False)
        self.service.boss.call_command('pastemanager', 'post_annotation', paste=self.__pastebin)

    def on_clear_button__clicked(self,but):
        '''Clears the paste'''
        self.__clear()
        
    def on_close_button__clicked(self,but):
        '''Quits the paste editor without modification'''
        self.close()

class paste_editor(service.service):

    multi_view_book = 'view'
    
    def init(self):
        pass

    def cmd_create_paste(self,paste):
        self.multi_view_type = paste_editor_view
        view = self.create_multi_view()
        view.set_paste_bin(paste)

    def cmd_view_paste(self,paste):
        self.multi_view_type = paste_viewer_view
        view = self.create_multi_view()
        view.set_paste(paste)

    def cmd_annotate_paste(self,paste):
        self.multi_view_type = paste_annotate_view
        view = self.create_multi_view()
        view.set_paste_bin(paste)

Service = paste_editor

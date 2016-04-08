#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016  Utkarsh Tiwari
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Utkarsh Tiwari    iamutkarshtiwari@gmail.com

import os
import dbus
import cairo
import logging
import StringIO
import tempfile
from gettext import gettext as _

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio

from sugar3 import env

from sugar3.datastore import datastore
from sugar3.graphics.icon import Icon
from sugar3.graphics import style
from sugar3.graphics.alert import Alert, TimeoutAlert
from sugar3.graphics import iconentry


from jarabe.model.session import get_session_manager
from jarabe.screenshotpanel.toolbar import MainToolbar
from jarabe import config
from jarabe.model import shell


_logger = logging.getLogger('SaveAsPanel')


class SaveAsPanel(Gtk.Window):
    '''
    Generates a pop papel to allow user to save the
    screenshot by the name of his choice
    '''

    __gtype_name__ = 'SaveAsPanel'


    def __init__(self):
        Gtk.Window.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
                                  style.COLOR_BLACK.get_gdk_color())
        self._set_screensize()
        self.set_border_width(style.LINE_WIDTH)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_can_focus(True)

        self.connect('key-press-event', self.__key_press_event_cb)

        self._toolbar = None
        self._canvas = None
        self._table = None
        self._scrolledwindow = None
        self._separator = None
        self._section_view = None
        self._section_toolbar = None
        self._main_toolbar = None

        self._vbox = Gtk.VBox()
        #self._hbox = Gtk.HBox()
        #self._vbox.pack_start(self._hbox, True, True, 0)
        #self._hbox.show()

        self._main_view = Gtk.EventBox()
        self._vbox.pack_start(self._main_view, True, True, 0)
        self._main_view.modify_bg(Gtk.StateType.NORMAL,
                                  style.COLOR_BLACK.get_gdk_color())
        self._main_view.show()

        self.add(self._vbox)
        self._vbox.show()
        self._setup_main()
        self._show_main_view()

        

        # Name label
        name_label = Gtk.Label()
        name_label.set_alignment(0.5, 1)
        name_label.set_use_markup(True)
        name_label.set_markup("<b>"+_('Name')+"</b>")
        name_label.modify_bg(Gtk.StateType.NORMAL,
                                  style.COLOR_BLACK.get_gdk_color())
        name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("yellow"))
        self._vbox.pack_start(name_label, True, True, 0)
        name_label.show()

        # Name entry box
        self._name_view = Gtk.EventBox()
        self._name_view.modify_bg(Gtk.StateType.NORMAL,
                                  style.COLOR_BLACK.get_gdk_color())
        self._name_view.show()

        # Entry box
        self._search_entry = Gtk.Entry()
        halign = Gtk.Alignment.new(0.5, 0, 0, 0)
        halign.add(self._name_view)
        halign.show()

        self._vbox.pack_start(halign, True, True, 0)
        self._name_view.add(self._search_entry)
        self._search_entry.show()
        #self._search_entry.set_text(_(activity_title))
        self._search_entry.grab_focus()
        self.show()

    def _set_cursor(self, cursor):
        self.get_window().set_cursor(cursor)
        Gdk.flush()

    def _set_screensize(self):
        '''
        Sets the size of the popup based on
        the screen resolution.
        '''
        width = Gdk.Screen.width() / 4
        height = Gdk.Screen.height() / 5
        self.set_size_request(width, height)

    def _set_toolbar(self, toolbar):
        '''
        Sets up the toolbar on the popup.
        '''
        if self._toolbar:
            self._vbox.remove(self._toolbar)
        self._vbox.pack_start(toolbar, False, False, 0)
        self._vbox.reorder_child(toolbar, 0)
        self._toolbar = toolbar
        if not self._separator:
            self._separator = Gtk.HSeparator()
            self._vbox.pack_start(self._separator, False, False, 0)
            self._vbox.reorder_child(self._separator, 1)
            self._separator.show()

    def _setup_main(self):
        self._main_toolbar = MainToolbar()
        self._main_toolbar.connect('stop-clicked',
                                   self.__stop_clicked_cb)
        #self._main_toolbar.connect('ok-clicked', self.__ok_clicked_cb)

    def _show_main_view(self):
        self._set_toolbar(self._main_toolbar)
        self._main_toolbar.show()
        self._main_view.modify_bg(Gtk.StateType.NORMAL,
                                  style.COLOR_BLACK.get_gdk_color())

    def __key_press_event_cb(self, window, event):
        if event.keyval == Gdk.KEY_Return:
            #self.save_screenshot(self._search_entry.get_text())
            self.destroy()
            return True

        if event.keyval == Gdk.KEY_Escape:
            if self._toolbar == self._main_toolbar:
                self.__stop_clicked_cb(None)
                self.destroy()
            return True

        # if the user clicked out of the window - fix SL #3188
        if not self.is_active():
            self.present()
        return False

    def __stop_clicked_cb(self, widget):
        self.destroy()

    def __ok_clicked_cb(self, widget):
        #self.save_screenshot(self._search_entry.get_text())
        self.destroy()

    

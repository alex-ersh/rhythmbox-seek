#
# Rythmbox Plugin to add menu items (and keyboard
# shortcuts) to seek forward (10 secs) / backward (5 secs)
# in the currently playing track.
#
# VERSION 1.0
#

# Copyright 2013 Cathal Garvey. http://cgarvey.ie/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from gi.repository import GObject, RB, Peas
from gi.repository import Gtk, Gio, GLib, Gdk


SEEK_BACKWARD_TIME = 5
SEEK_FORWARD_TIME = 10


class TrackSeekPlugin(GObject.Object, Peas.Activatable):
    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        super(TrackSeekPlugin, self).__init__()
        self.fwd_action_name = "SeekPluginForward"
        self.fwd_menu_name = "Seek _Forward"
        self.fwd_accel = "<shift>Right"
        self.bwd_action_name = "SeekPluginBackward"
        self.bwd_menu_name = "Seek _Backward"
        self.bwd_accel = "<shift>Left"

    def add_action(self, action_name, menu_name, accel, func):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", func)
        self.object.props.window.add_action(action)

        item = Gio.MenuItem()
        item.set_detailed_action("win." + action_name)
        item.set_label(menu_name)
        item.set_attribute_value("accel", GLib.Variant("s", accel))

        app = Gio.Application.get_default()
        app.add_plugin_menu_item("tools", "tools" + action_name, item)
        app.set_accels_for_action("win." + action_name, [accel])

    def remove_action(self, action_name):
        app = Gio.Application.get_default()
        app.set_accels_for_action("win." + action_name, [])
        app.remove_plugin_menu_item("tools", "tools" + action_name)
        self.object.props.window.remove_action(action_name)

    def do_activate(self):
        print("Activating Plugin")
        self.add_action(self.bwd_action_name, self.bwd_menu_name,
                        self.bwd_accel, self.on_skip_backward)
        self.add_action(self.fwd_action_name, self.fwd_menu_name,
                        self.fwd_accel, self.on_skip_forward)

    def on_skip_backward(self, *args):
        print("Seeking backward")
        sp = self.object.props.shell_player

        if sp.get_playing()[1]:
            seek_time = sp.get_playing_time()[1] - SEEK_BACKWARD_TIME
            if seek_time < 0:
                seek_time = 0

            print("Seeking backward to {0} sec(s)".format(seek_time))
            sp.set_playing_time(seek_time)
            print("Done.")
        else: print("Not playing, refusing to seek backward")

    def on_skip_forward(self, *args):
        print("Seeking forward")
        sp = self.object.props.shell_player

        if sp.get_playing()[1]:
            seek_time = sp.get_playing_time()[1] + SEEK_FORWARD_TIME
            song_duration = sp.get_playing_song_duration()
            if song_duration > 0: #sanity check
                if seek_time > song_duration:
                    seek_time = song_duration

                print("Seeking forward to {0} sec(s)".format(seek_time))
                sp.set_playing_time(seek_time)
                print("Done.")
            else: print("Song duration is reported as 0. Refusing to seek!")
        else: print("Not playing, refusing to seek forward")

    def do_deactivate(self):
        print("De-activating Plugin")
        self.remove_action(self.fwd_action_name)
        self.remove_action(self.bwd_action_name)


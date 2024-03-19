#!/usr/bin/env python
"""
Usage

    media_player.py [options] <filename>

Query and play the video.
"""

import time
from query_match import initialize, match
from query_match_rgb import initialize_rgb, match_rgb
import pyglet
from pyglet.gl import *
import weakref
import sys

__docformat__ = 'restructuredtext'

VIDEO = "INITIAL_INVALID_VIDEO_FILE_NAME"
START_INDEX = -1


def draw_rect(x, y, width, height, color=(1, 1, 1, 1)):
    pyglet.graphics.draw(
        4,
        GL_LINE_LOOP,
        position=('f', (x, y, 0,
                        x + width, y, 0,
                        x + width, y + height, 0,
                        x, y + height, 0,
                        )
                  ),
        colors=('f', color * 4)
    )


class Control(pyglet.event.EventDispatcher):
    x = y = 0
    width = height = 10

    def __init__(self, parent):
        super(Control, self).__init__()
        self.parent = weakref.proxy(parent)

    def hit_test(self, x, y):
        return (self.x < x < self.x + self.width and
                self.y < y < self.y + self.height)

    def capture_events(self):
        self.parent.push_handlers(self)

    def release_events(self):
        self.parent.remove_handlers(self)


class Button(Control):
    charged = False

    def draw(self):
        if self.charged:
            draw_rect(self.x, self.y, self.width, self.height)
        else:
            draw_rect(self.x, self.y, self.width,
                      self.height, color=(1, 0, 0, 1))
        self.draw_label()

    def on_mouse_press(self, x, y, button, modifiers):
        self.capture_events()
        self.charged = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.charged = self.hit_test(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        if self.hit_test(x, y):
            self.dispatch_event('on_press')
        self.charged = False


Button.register_event_type('on_press')


class TextButton(Button):
    def __init__(self, *args, **kwargs):
        super(TextButton, self).__init__(*args, **kwargs)
        self._text = pyglet.text.Label(
            '', anchor_x='center', anchor_y='center')

    def draw_label(self):
        self._text.x = self.x + self.width / 2
        self._text.y = self.y + self.height / 2
        self._text.draw()

    def set_text(self, text):
        self._text.text = text

    text = property(lambda self: self._text.text,
                    set_text)


class PlayerWindow(pyglet.window.Window):
    GUI_WIDTH = 400
    GUI_HEIGHT = 40
    GUI_PADDING = 4
    GUI_BUTTON_HEIGHT = 16

    def __init__(self, player):
        super(PlayerWindow, self).__init__(caption='Media Player',
                                           visible=False,
                                           resizable=True)
        # We only keep a weakref to player as we are about to push ourself
        # as a handler which would then create a circular reference between
        # player and window.
        self.player = player  # weakref.proxy(player)
        self._player_playing = False
        self.player.push_handlers(self)

        self.play_button = TextButton(self)
        self.play_button.x = self.GUI_PADDING
        self.play_button.y = self.GUI_PADDING
        self.play_button.height = self.GUI_BUTTON_HEIGHT
        self.play_button.width = 60
        self.play_button.on_press = self.on_play
        self.play_button.text = 'Play'

        self.pause_button = TextButton(self)
        self.pause_button.x = self.play_button.x + \
            self.play_button.width + self.GUI_PADDING
        self.pause_button.y = self.GUI_PADDING
        self.pause_button.height = self.GUI_BUTTON_HEIGHT
        self.pause_button.width = 60
        self.pause_button.on_press = self.on_pause
        self.pause_button.text = 'Pause'

        self.reset_button = TextButton(self)
        self.reset_button.x = self.pause_button.x + \
            self.pause_button.width + self.GUI_PADDING
        self.reset_button.y = self.GUI_PADDING
        self.reset_button.height = self.GUI_BUTTON_HEIGHT
        self.reset_button.width = 60
        self.reset_button.on_press = self.on_reset
        self.reset_button.text = 'Reset'

        self.query_reset_button = TextButton(self)
        self.query_reset_button.x = self.reset_button.x + \
            self.reset_button.width + self.GUI_PADDING
        self.query_reset_button.y = self.GUI_PADDING
        self.query_reset_button.height = self.GUI_BUTTON_HEIGHT
        self.query_reset_button.width = 60
        self.query_reset_button.on_press = self.on_query_reset
        self.query_reset_button.text = 'Query'

        self.controls = [
            self.play_button,
            self.pause_button,
            self.reset_button,
            self.query_reset_button,
        ]

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def on_eos(self):
        self.on_reset()
        return True

    def get_video_size(self):
        if not self.player.source or not self.player.source.video_format:
            print("No video")
            return 0, 0
        video_format = self.player.source.video_format
        width = video_format.width
        height = video_format.height
        if video_format.sample_aspect > 1:
            width *= video_format.sample_aspect
        elif video_format.sample_aspect < 1:
            height /= video_format.sample_aspect
        return width, height

    def set_default_video_size(self):
        """Make the window size just big enough to show the current
        video and the GUI."""
        width = self.GUI_WIDTH
        height = self.GUI_HEIGHT
        video_width, video_height = self.get_video_size()
        width = max(width, video_width)
        height += video_height
        self.set_size(int(width), int(height))

    def on_resize(self, width, height):
        """Position and size video image."""
        super(PlayerWindow, self).on_resize(width, height)

        height -= self.GUI_HEIGHT
        if height <= 0:
            return

        video_width, video_height = self.get_video_size()
        if video_width == 0 or video_height == 0:
            return
        display_aspect = width / float(height)
        video_aspect = video_width / float(video_height)
        if video_aspect > display_aspect:
            self.video_width = width
            self.video_height = width / video_aspect
        else:
            self.video_height = height
            self.video_width = height * video_aspect
        self.video_x = (width - self.video_width) / 2
        self.video_y = (height - self.video_height) / 2 + self.GUI_HEIGHT

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self.controls:
            if control.hit_test(x, y):
                control.on_mouse_press(x, y, button, modifiers)

    def on_close(self):
        self.player.pause()
        self.close()

    def auto_close(self, dt):
        self.close()

    def on_play(self):
        if not self.player.playing:
            self.player.play()

    def on_pause(self):
        if self.player.playing:
            self.player.pause()

    def on_reset(self):
        self.player.seek(1/30)
        self.on_pause()

    def on_query_reset(self):
        self.player.seek(START_INDEX/30)
        self.on_pause()

    def on_draw(self):
        self.clear()
        # Video
        if self.player.source and self.player.source.video_format:
            self.player.get_texture().blit(self.video_x,
                                           self.video_y,
                                           width=self.video_width,
                                           height=self.video_height)
        # GUI
        for control in self.controls:
            control.draw()


def usage():
    print(__doc__)
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    VIDEO = sys.argv[1]
    query_path = VIDEO
    if sys.argv[1].endswith(".rgb"):
        initialize_rgb('./CSCI576_features_rgb.pkl')
    else:
        initialize('./CSCI576_features.pkl')
    t = time.time()
    result = match_rgb(query_path) if VIDEO.endswith(
        ".rgb") else match(query_path)
    print("{:.4f} second for the query".format(time.time() - t))

    if result[0] is None:
        print("No match found")
        sys.exit(1)

    player = pyglet.media.Player()
    window = PlayerWindow(player)
    player.queue(pyglet.media.load("Dataset/video" + str(result[0]) + ".mp4"))
    window.set_visible(True)
    window.set_default_video_size()
    START_INDEX = result[1] if VIDEO.endswith(".mp4") else result[1] + 1
    player.seek(START_INDEX / 30)
    pyglet.app.run()

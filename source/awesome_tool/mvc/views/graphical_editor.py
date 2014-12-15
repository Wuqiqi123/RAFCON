
from utils import log
logger = log.get_logger(__name__)

import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
# Activate the following line in the production code th increase speed
# http://pyopengl.sourceforge.net/documentation/opengl_diffs.html:
# OpenGL.ERROR_CHECKING = False
OpenGL.FULL_LOGGING = True
# Also in productive code, set the previous statement to false and activate the next one
# OpenGL.ERROR_LOGGING = False

import gtk
import gtk.gtkgl
from gtkmvc import View


class GraphicalEditorView(View):


    def __init__(self):
        View.__init__(self)

        # Configure OpenGL framebuffer.
        # Try to get a double-buffered framebuffer configuration,
        # if not successful then exit program
        display_mode = (gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_SINGLE)
        try:
            glconfig = gtk.gdkgl.Config(mode=display_mode)
        except gtk.gdkgl.NoMatches:
            raise SystemExit

        self.win = gtk.Window()
        self.win.set_title("Graphical Editor")
        self.v_box = gtk.VBox()
        self.test_label = gtk.Label("Hallo")
        self.editor = GraphicalEditor(glconfig)
        self.editor.set_size_request(200, 200)

        self.v_box.pack_start(self.test_label)
        self.v_box.pack_end(self.editor)

        self.win.add(self.v_box)
        self.win.show_all()
        self.win.connect("destroy", lambda w: gtk.main_quit())

        # Query the OpenGL extension version.
        print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()


    def get_top_widget(self):
        return self.win


class GraphicalEditor(gtk.DrawingArea, gtk.gtkgl.Widget):

    def __init__(self, glconfig):
        gtk.DrawingArea.__init__(self)

        # Set OpenGL-capability to the drawing area
        self.set_gl_capability(glconfig)

        # Connect the relevant signals.
        self.connect_after('realize',   self._on_realize)
        self.connect('configure_event', self._on_configure_event)
        self.connect('expose_event',    self._on_expose_event)

    def _on_realize(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        # gldrawable = self.get_gl_drawable()
        # glcontext = self.get_gl_context()

        glClearColor(0, 1, 0, 0.5)

        logger.debug("realize")

    def _on_configure_event(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        logger.debug("configure")

        # OpenGL begin
        if not gldrawable.gl_begin(glcontext):
            return False

        glViewport(0, 0, self.allocation.width, self.allocation.height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.allocation.width/float(self.allocation.height)
        print aspect
        if self.allocation.width <= self.allocation.height:
            glOrtho(-100, 100, -100/aspect, 100/aspect, 1, -1)
        else:
            glOrtho(-100*aspect, 100*aspect, -100, 100, 1, -1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # OpenGL end
        gldrawable.gl_end()

        return False

    def _on_expose_event(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        # OpenGL begin
        if not gldrawable.gl_begin(glcontext):
            return False

        logger.debug("expose")

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glColor4f(1, 0, 0, 0.5)
        glRectf(-25, 25, 25, -25)

        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()

        # OpenGL end
        gldrawable.gl_end()

        return False

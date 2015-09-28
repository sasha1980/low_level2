#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Здесь показывается как нужно создавть OpenGL контекст в GTK
# [2015-09-24]
# 1. + Всё работает

import gc, pygtk, gtk, gtk.gdkgl#, glfw

from OpenGL.GL import *
from OpenGL.GLU import *



def on_quit (*args):
	pass


def on_realize (*args):
	#print "on_realize()", args
	drawing_area = args[0]
	# Add OpenGL API support to self.window
	gtk.gdkgl.ext(drawing_area.window)
	# Add OpenGL-capability to self.window, and get the OpenGL drawable.
	drawing_area.gldrawable = drawing_area.window.set_gl_capability (drawing_area.glconfig)
	# Then create an OpenGL rendering context.
	if not drawing_area.glcontext:
		drawing_area.glcontext = gtk.gdkgl.Context(drawing_area.gldrawable)
		if not drawing_area.glcontext:
			raise SystemExit, "** Cannot create OpenGL rendering context!"
		print "OpenGL rendering context is created."
	# OpenGL begin.
	if not drawing_area.gldrawable.gl_begin(drawing_area.glcontext):
		return

	glEnable(GL_MULTISAMPLE)


	#glfwWindowHint (GLFW_SAMPLES, 4)

	light_diffuse = (1.0, 0.0, 0.0, 1.0)
	light_position = (1.0, 1.0, 1.0, 0.0)
	qobj = gluNewQuadric()

	gluQuadricDrawStyle(qobj, GLU_FILL)
	glNewList(1, GL_COMPILE)
	gluSphere(qobj, 1.0, 20, 20)
	glEndList()

	glNewList(2, GL_COMPILE)
	glEndList()


	glNewList (3, GL_COMPILE)
	glCallList (1)
	glEndList ()


	glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
	glLightfv(GL_LIGHT0, GL_POSITION, light_position)

	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_DEPTH_TEST)

	glClearColor(1.0, 1.0, 1.0, 1.0)
	glClearDepth(1.0)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(120.0, 1.0, 1.0, 10.0)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluLookAt (0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
	glTranslatef (1.5, -1.5, -3.0)
	drawing_area.gldrawable.gl_end()

def on_size_allocate (*args):
	#print "on_size_allocate()", args
	drawing_area = args[0]
	if drawing_area.gldrawable:
		drawing_area.gldrawable.wait_gdk()


def on_configure_event (*args):
	#print "on_configure_event()", args
	drawing_area = args[0]
	# GtkDrawingArea sends a configure event when it's being realized. So
	# we'll wait till it's been fully realized.
	if not drawing_area.gldrawable:
		return False
	if not drawing_area.gldrawable.gl_begin(drawing_area.glcontext):
		return False
	glViewport(0, 0, drawing_area.allocation.width, drawing_area.allocation.height)
	drawing_area.gldrawable.gl_end()
	return False

def on_expose_event (*args):
	#print "on_expose_event()", args
	drawing_area = args[0]
	if drawing_area.gldrawable is None:
		return False
	if not drawing_area.gldrawable.gl_begin(drawing_area.glcontext):
		return False
	glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glCallList (3)
	if drawing_area.gldrawable.is_double_buffered():
		drawing_area.gldrawable.swap_buffers()
	else:
		glFlush()
	drawing_area.gldrawable.gl_end()
	return False

def on_unrealize (*args):
	#print "on_unrealize()", args
	drawing_area = args[0]
	# Remove OpenGL-capability
	drawing_area.window.unset_gl_capability()
	# Unref
	drawing_area.gldrawable = None
	drawing_area.glcontext = None
	gc.collect()

frame = 0
def on_timer_tick (*args):
	#print "on_timer_tick ()", args
	global frame
	drawing_area = args[0]
	if drawing_area.window is None:
		return True

	alloc = drawing_area.get_allocation()
	rect = gtk.gdk.Rectangle (0, 0, alloc.width, alloc.height)
	drawing_area.window.invalidate_rect (rect, True)
	drawing_area.window.process_updates (True)

	frame += 1
	frame %= 2
	glNewList (3, GL_COMPILE)
	glCallList (1 + frame)
	glEndList ()

	return True

pygtk.require('2.0')

gtk_window = gtk.Window()
gtk_window.set_title('low-level')
gtk_window.set_reallocate_redraws (True)
gtk_window.connect ('delete_event', gtk.main_quit)
vbox = gtk.VBox()
gtk_window.add (vbox)
display_mode = gtk.gdkgl.MODE_RGBA | gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE | gtk.gdkgl.MODE_MULTISAMPLE
glconfig = gtk.gdkgl.Config (mode = display_mode)
drawing_area = gtk.DrawingArea ()
drawing_area.set_double_buffered(False)
drawing_area.glconfig = glconfig
drawing_area.gldrawable = None
drawing_area.glcontext = None



drawing_area.connect_after ('realize', on_realize)
drawing_area.connect ('size_allocate', on_size_allocate)
drawing_area.connect ('configure_event', on_configure_event)
drawing_area.connect ('expose_event', on_expose_event)
drawing_area.connect ('unrealize', on_unrealize)

drawing_area.set_size_request (1280, 720)
vbox.pack_start (drawing_area)
gtk.quit_add (gtk.main_level() + 1, on_quit, drawing_area)
button1 = gtk.Button ('Quit')
button1.connect ('clicked', gtk.main_quit)
vbox.pack_start(button1, expand = False)

gtk.timeout_add (10, on_timer_tick, drawing_area)

gtk_window.show_all()
gtk.main()

# cellmodel.py
#
# Micropolis, Unix Version.  This game was released for the Unix platform
# in or about 1990 and has been modified for inclusion in the One Laptop
# Per Child program.  Copyright (C) 1989 - 2007 Electronic Arts Inc.  If
# you need assistance with this program, you may contact:
#   http://wiki.laptop.org/go/Micropolis  or email  micropolis@laptop.org.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.  You should have received a
# copy of the GNU General Public License along with this program.  If
# not, see <http://www.gnu.org/licenses/>.
#
#             ADDITIONAL TERMS per GNU GPL Section 7
#
# No trademark or publicity rights are granted.  This license does NOT
# give you any right, title or interest in the trademark SimCity or any
# other Electronic Arts trademark.  You may not distribute any
# modification of this program using the trademark SimCity or claim any
# affliation or association with Electronic Arts Inc. or its employees.
#
# Any propagation or conveyance of this program must include this
# copyright notice and these terms.
#
# If you convey this program (or any modifications of it) and assume
# contractual liability for the program to recipients of it, you agree
# to indemnify Electronic Arts for any liability that those contractual
# assumptions impose on Electronic Arts.
#
# You may not misrepresent the origins of this program; modified
# versions of the program must be marked as such and not identified as
# the original program.
#
# This disclaimer supplements the one included in the General Public
# License.  TO THE FULLEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW, THIS
# PROGRAM IS PROVIDED TO YOU "AS IS," WITH ALL FAULTS, WITHOUT WARRANTY
# OF ANY KIND, AND YOUR USE IS AT YOUR SOLE RISK.  THE ENTIRE RISK OF
# SATISFACTORY QUALITY AND PERFORMANCE RESIDES WITH YOU.  ELECTRONIC ARTS
# DISCLAIMS ANY AND ALL EXPRESS, IMPLIED OR STATUTORY WARRANTIES,
# INCLUDING IMPLIED WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY,
# FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT OF THIRD PARTY
# RIGHTS, AND WARRANTIES (IF ANY) ARISING FROM A COURSE OF DEALING,
# USAGE, OR TRADE PRACTICE.  ELECTRONIC ARTS DOES NOT WARRANT AGAINST
# INTERFERENCE WITH YOUR ENJOYMENT OF THE PROGRAM; THAT THE PROGRAM WILL
# MEET YOUR REQUIREMENTS; THAT OPERATION OF THE PROGRAM WILL BE
# UNINTERRUPTED OR ERROR-FREE, OR THAT THE PROGRAM WILL BE COMPATIBLE
# WITH THIRD PARTY SOFTWARE OR THAT ANY ERRORS IN THE PROGRAM WILL BE
# CORRECTED.  NO ORAL OR WRITTEN ADVICE PROVIDED BY ELECTRONIC ARTS OR
# ANY AUTHORIZED REPRESENTATIVE SHALL CREATE A WARRANTY.  SOME
# JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF OR LIMITATIONS ON IMPLIED
# WARRANTIES OR THE LIMITATIONS ON THE APPLICABLE STATUTORY RIGHTS OF A
# CONSUMER, SO SOME OR ALL OF THE ABOVE EXCLUSIONS AND LIMITATIONS MAY
# NOT APPLY TO YOU.


########################################################################
# Cellular Automata Machine Model
# Don Hopkins


########################################################################
# Import stuff


import sys
import os
import time
import random
import cellengine
import gobject
import cairo
from pyMicropolis.cellEngine import cellengine
import xml.dom.minidom
from xml.dom.minidom import Node
import pprint
from StringIO import StringIO


########################################################################
# Globals


__version__ = "0.9"


########################################################################
# Utilities


def GetElementText(el, default=u''):
    if not el:
        return default
    text = default
    foundText = False
    el = el.firstChild
    while el:
        if el.nodeType == el.TEXT_NODE:
            value = el.nodeValue
            if not foundText:
                # Replace the default with the first text.
                foundText = True
                text = value
            else:
                text += value
        el = el.nextSibling
    return text


def GetElementBool(el, default=False):
    if not el:
        return default
    text = GetElementText(el).lower()
    if text == 'true':
        return True
    if text == 'false':
        return False
    return default


def GetElementInt(el, default=0):
    if not el:
        return default
    try:
        val = int(GetElementText(el))
    except:
        val = default
    return val


def GetElementFloat(el, default=0.0):
    if not el:
        return default
    try:
        val = float(GetElementText(el))
    except:
        val = default
    return val


def GetSubElement(el, key):
    # Isn't there a faster way to do this? (Only searching direct children.)
    el = el.firstChild
    while el:
        if ((el.nodeType == el.ELEMENT_NODE) and
            (el.nodeName == key)):
            return el
        el = el.nextSibling
    return None


def GetSubElementText(el, key, default=u''):
    return GetElementText(GetSubElement(el, key), default)


def GetSubElementBool(el, key, default=False):
    return GetElementBool(GetSubElement(el, key), default)


def GetSubElementInt(el, key, default=0):
    return GetElementInt(GetSubElement(el, key), default)


def GetSubElementFloat(el, key, default=0.0):
    return GetElementFloat(GetSubElement(el, key), default)


def SetSubElementText(el, key, value):
    subEl = el.createElement(key)
    text = el.createTextNode(value)
    subEl.appendChild(text)
    el.appendChild(subEl)


def SetSubElementBool(el, key, value):
    if value:
        value = 'true'
    else:
        value = 'false'
    SetSubElementText(el, key, value)


def SetSubElementInt(el, key, value):
    SetSubElementText(el, key, str(value))


def SetSubElementFloat(el, key, value):
    SetSubElementText(el, key, str(value))


########################################################################
# CellModel Class


class CellModel(cellengine.CellEngine):


    def __init__(
            self,
            running=True,
            timeDelay=100,
            *args,
            **kwargs):

        cellengine.CellEngine.__init__(self, *args, **kwargs)

        self.running = running
        self.timeDelay = timeDelay
        self.timerActive = False
        self.timerId = None
        self.views = []


        if self.running:
            self.startTimer()

        #print "CellModel.__init__ done", self


    def __del__(
        self):

        self.stopTimer()

        cellengine.Cell.__del__(self)


    def addView(self, view):
        views = self.views
        if view not in views:
            self.views.append(view)
            print "ADDVIEW", view


    def removeView(self, view):
        views = self.views
        if view in views:
            views.remove(view)
            print "REMOVEVIEW", view


    def startTimer(
        self):

        if self.timerActive:
            return

        self.timerId = gobject.timeout_add(self.timeDelay, self.tickTimer)
        self.timerActive = True


    def stopTimer(
        self):

        # FIXME: Is there some way to immediately cancel self.timerId?

        self.timerActive = False


    def tickTimer(
        self):

        if not self.timerActive:
            return False

        self.stopTimer()

        self.tickEngine()

        for view in self.views:
            view.tickActiveTool()

        for view in self.views:
            view.tickTimer()

        if self.running:
            self.startTimer()

        return False


    def tickEngine(self):

        self.DoRule()
        self.updateViews()


    def updateViews(self):
        for view in self.views:
            view.updateView()


    def __repr__(self):
        return "<CellModel>"


########################################################################


def CreateTestEngine():

    # Get our nice scriptable subclass of the SWIG CellEngine wrapper object.
    engine = CellModel()

    w = 256
    h = 256

    engine.InitScreen(w, h)
    engine.SetRect(0, 0, w, h)
    engine.wrap = 3
    engine.steps = 1
    engine.frob = 5
    engine.neighborhood = 46
    #engine.neighborhood = 37
    #engine.LoadRule('WORMS')
    engine.Garble()

    return engine


########################################################################

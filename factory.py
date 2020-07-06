# -------- Program Overview: -------- #
# Factory is a game created in Python. The objective of the game is to create increasingly complicated
# assembly lines in a factory in order to manufacture & sell increasingly complicated products.

# -------- Program Notes: -------- #
# Each tile fits one machine and is made up of 25x25 pixels.
# Objects are held in lists of Machines, Materials, & Tiles.
# Coreloop loop runs atd interval
# Iterate through list of machines and perform actions
# Iterate through list of materials and perform actions
# Material instances created and appended to Materials list as needed
# Buttons and menu actions run as interrupts
# The grid origin is the bottom left corner and scene origin is the top left corner
# Materials will group together with visual offsets when they are stacked

# -------- GUI Layout Structure: -------- #
# app QApplication
# mainApp (QMainWindow)
#     mainWidget (QWidget)[mainVLayout] *centralWidget*
#         Top Dock Widget(QWidget)
#         container (QWidget)  - [containerGrid (QGridLayout(1x1))]
#             viewFrame (QGraphicsView)
#             buildMenuFrame (QFrame)
#             blueprintsMenuFrame (QFrame)
#             etc...
#         Bottom Dock Widget(QWidget)


# -------- Imports -------- #
from PyQt5 import QtCore, QtWidgets, QtGui
import datetime
import math
import pickle
from factoryLib import *  # Usage: mainApp.lib.machineLib[STARTER]
from win32api import GetSystemMetrics  # Only used to detect monitor setup
import sys
import traceback
import time
import statistics
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from termcolor import colored
import logging

# -------- Constants -------- #

CYCLE_INTERVAL = 25  # Core loop time (ms) 25 = 1 roller/sec, 40 = 25fps, 17 = 60fps
MAT_LAUNCH_INTERVAL = 40  # Iterations between material launches
INCOME_ANALYSIS_FREQ = 10
FRAME_RATE_ANALYSIS_LOG_SIZE = 600
GRID_SIZE = 25
MACHINE_SIZE = 24
MAT_SIZE = 8
TIME_PROFILE_ALARM_LIMIT = 37
TIME_PROFILE_ZERO_FLOOR = 0.001
ORIENTATIONS = ['U', 'L', 'D', 'R']
ANGLE = {'U': 180, 'L': 90, 'D': 0, 'R': 270}
VISUAL_OFFSET_1_TO_2 = [(0, 0), (2, 0)]  # Visual offsets for groups of size 1 to 2 materials
VISUAL_OFFSET_3_TO_3 = [(-2, 0), (0, 2), (2, 0)]
VISUAL_OFFSET_4_TO_4 = [(-2, 2), (2, 2), (-2, -2), (2, -2)]
VISUAL_OFFSET_5_TO_9 = [(0, 0), (2, 0), (-2, 0),
                        (0, -2), (2, -2), (-2, -2),
                        (0, 2), (2, 2), (-2, 2)]
RESET_QUEUED = True
RESET_NOT_QUEUED = False
IN = 'In'
OUT = 'Out'
LEFT = 'Left'
RIGHT = 'Right'
ARM = 'Arm'
RESET = 'Reset'
WALLED = True
NOT_WALLED = False
LOCKED = True
NOT_LOCKED = False
LOCK = 'Lock'  # drawShape argument flag
WALL = 'Wall'
HIGHLIGHT = 'Highlight'
Z_MACHINE_BOTTOM = 0  # Z Height Stack Order
Z_MATERIAL = 1
Z_MACHINE_TOP = 2
Z_PICKED_UP = 3
Z_ROBOT_ARM = 4
Z_ARROW = 5
Z_HIGHLIGHT = 6
STARTER = 'Starter'
CRAFTER = 'Crafter'
SELLER = 'Seller'
ROLLER = 'Roller'
DRAWER = 'Drawer'
CUTTER = 'Cutter'
FURNACE = 'Furnace'
PRESS = 'Press'
SPLITTER_LEFT = 'Splitter Left'
SPLITTER_RIGHT = 'Splitter Right'
SPLITTER_TEE = 'Splitter Tee'
SPLITTER_3WAY = 'Splitter 3-Way'
FILTER_LEFT = 'Filter Left'
FILTER_RIGHT = 'Filter Right'
FILTER_TEE = 'Filter Tee'
ROBOTIC_ARM = 'Robotic Arm'
FILTERED_ARM = 'Filtered Arm'
TELEPORTER_INPUT = 'Teleporter Input'
TELEPORTER_OUTPUT = 'Teleporter Output'


# Logger
_LOGGER = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)  # Print debug and higher
# logging.basicConfig(level=logging.ERROR)  # Print error and higher


# -------- Classes -------- #

class QLabelT(QtWidgets.QLabel):  # Black BG, Larger Font
    def __init__(self, parent=None):
        super(QLabelT, self).__init__(parent)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.setFont(font)
        self.setMinimumHeight(60)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet('background:rgb(243, 243, 243);\
                           color: black;\
                           border: 0px solid black')


class QLabelImgA(QtWidgets.QLabel):
    def __init__(self, parent=None, pixmap=None, styleSet=None, fixedWidth=None):
        super(QLabelImgA, self).__init__(parent)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.setFont(font)
        if fixedWidth is not None:
            self.setFixedWidth(fixedWidth)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setPixmap(pixmap)
        if styleSet == 'White-Square':  # White BG, Square Border
            self.setStyleSheet('border: 1px solid black;\
                               background-color : white;\
                               color : black;\
                               padding: 2px')
        elif styleSet == 'Blue-None':  # Blue BG, No Border
            self.setStyleSheet('border: 0px solid black;\
                               background-color: steelblue;\
                               color: black;\
                               padding: 2px')
        elif styleSet == 'White-None':  # White BG, No Border
            self.setStyleSheet('border: 0px solid black;\
                               background-color: white;\
                               color: black;\
                               padding: 2px')
        elif styleSet == 'Gray-None':  # Gray BG, No Border
            self.setStyleSheet('border: 0px solid black;\
                               background-color: lightgray;\
                               color: black;\
                               padding: 2px')


class QLabelA(QtWidgets.QLabel):
    def __init__(self, parent=None, styleSet='White-Square', fixedWidth=None, fontSize=11):
        super(QLabelA, self).__init__(parent)
        font = QtGui.QFont()
        font.setPointSize(fontSize)
        self.setFont(font)
        self.setMinimumHeight(24)
        if fixedWidth is not None:
            self.setFixedWidth(fixedWidth)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleCode(styleSet)

    def setStyleCode(self, option):
        if option == 'White-Square':  # White BG, Square Border
            self.setStyleSheet('border: 1px solid black;\
                               background-color: white;\
                               color: black;\
                               padding: 2px')
        elif option == 'White-Square-Table':  # White BG, Square Bottom Border
            self.setStyleSheet('border-bottom: 1px solid gray;\
                                background-color: white;\
                                color: black;\
                                padding: 2px')
        elif option == 'White-Square-Table-Title':  # White BG, Square Top & Bottom Border
            self.setStyleSheet('border-top: 1px solid black;\
                                border-bottom: 1px solid black;\
                                background-color: white;\
                                color: black;\
                                font-weight: bold;\
                                padding: 2px')
        elif option == 'Gray-Square':  # Gray BG, Square Border
            self.setStyleSheet('border: 1px solid black;\
                               background-color: lightgray;\
                               color: black;\
                               padding: 2px')
        elif option == 'Light-Gray-Square':  # Light Gray BG, Square Border
            self.setStyleSheet('border: 1px solid black;\
                               background-color: rgb(243, 243, 243);\
                               color: black;\
                               padding: 2px')
        elif option == 'Green-Square':  # Green BG, White FG, Square Border
            self.setStyleSheet('border: 1px solid black;\
                               background-color: green;\
                               color: white;\
                               padding: 2px')
        elif option == 'Red-Square':  # Red BG, Square Border
            self.setStyleSheet('border: 1px solid black;\
                               background-color: tomato;\
                               color: black;\
                               padding: 2px')
        elif option == 'Blue-None':  # Blue BG, No Border
            self.setStyleSheet('border: 0px solid black;\
                               background-color: steelblue;\
                               color: white;\
                               padding: 2px')
        elif option == 'Gray-None':  # Gray BG, No Border
            self.setStyleSheet('border: 0px solid black;\
                                   background-color: lightgray;\
                                   color: black;\
                                   padding: 2px')
        elif option == 'Blue-None-White-Large':  # Blue BG, No Border, White Text Slightly Larger
            self.setStyleSheet('border: 0px solid black;\
                               background-color: steelblue;\
                               color: white;\
                               font-size: 24pt;\
                               padding: 2px')
        elif option == 'Green-None':  # Green BG, White FG, No Border
            self.setStyleSheet('border: 0px solid black;\
                               background-color: green;\
                               color: white;\
                               padding: 2px')
        elif option == 'White-None':  # White BG, No Border
            self.setStyleSheet('border: 0px solid black;\
                               background-color: white;\
                               color: black;\
                               padding: 2px')
        elif option == 'White-Round':  # White BG, Rounded Border
            self.setStyleSheet('border: 1px solid black;\
                               border-radius: 6;\
                               background-color: white;\
                               color: black;\
                               padding: 2px')
        elif option == 'Green-Round':  # Green BG, White FG, Rounded Border
            self.setStyleSheet('border: 1px solid black;\
                               border-radius: 6;\
                               background-color: green;\
                               color: white;\
                               padding: 2px')
        elif option == 'Red-Round':  # Red BG, Rounded Border
            self.setStyleSheet('border: 1px solid black;\
                               border-radius: 6;\
                               background-color: tomato;\
                               color: black;\
                               padding: 2px')
        elif option == 'Blue-Round':  # Blue BG, Rounded Border
            self.setStyleSheet('border: 1px solid black;\
                               border-radius: 6;\
                               background-color: steelblue;\
                               color: black;\
                               padding: 2px')
        elif option == 'LightGray-Round':  # LightGray BG, Rounded Border
            self.setStyleSheet('border: 1px solid black;\
                               border-radius: 6;\
                               background:rgb(243, 243, 243);\
                               color: black;\
                               padding: 2px')


class QPushButtonA(QtWidgets.QPushButton):
    def __init__(self, parent=None, styleSet='White-Square', fixedWidth=None, fontSize=11):
        super(QPushButtonA, self).__init__(parent)
        font = QtGui.QFont()
        font.setPointSize(fontSize)
        self.setFont(font)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setMinimumHeight(24)
        if fixedWidth is not None:
            self.setFixedWidth(fixedWidth)
        self.setStyleCode(styleSet)

    def setStyleCode(self, option):
        if option == 'OS':  # Gray OS Default
            pass
        elif option == 'White-Square-Menu-Left-Side':  # White BG, Square Partial Border For Main Menu Buttons
            self.setStyleSheet('QPushButton{\
                                border-top: 1px solid black;\
                                border-left: 1px solid black;\
                                background-color: white;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: lightgray}')
        elif option == 'White-Square-Menu-Right-Side':  # White BG, Square Partial Border For Main Menu Buttons
            self.setStyleSheet('QPushButton{\
                                border-top: 1px solid black;\
                                border-left: 1px solid black;\
                                border-right: 1px solid black;\
                                background-color: white;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: lightgray}')
        elif option == 'White-Square-Menu-Bottom-Side':  # White BG, Square Partial Border For Main Menu Buttons
            self.setStyleSheet('QPushButton{\
                                border-top: 1px solid black;\
                                border-left: 1px solid black;\
                                border-bottom: 1px solid black;\
                                background-color: white;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: lightgray}')
        elif option == 'Blue-Square-Menu-Left-Side':  # Blue BG, Square Partial Border For Main Menu Buttons
            self.setStyleSheet('QPushButton{\
                                border-top: 1px solid black;\
                                border-left: 1px solid black;\
                                background-color: steelblue;\
                                color: white;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: steelblue}')
        elif option == 'Blue-Square-Menu-Right-Side':  # Blue BG, Square Partial Border For Main Menu Buttons
            self.setStyleSheet('QPushButton{\
                                border-top: 1px solid black;\
                                border-left: 1px solid black;\
                                border-right: 1px solid black;\
                                background-color: steelblue;\
                                color: white;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: steelblue}')
        elif option == 'Blue-Square-Menu-Bottom-Side':  # Blue BG, Square Partial Border For Main Menu Buttons
            self.setStyleSheet('QPushButton{\
                                border-top: 1px solid black;\
                                border-left: 1px solid black;\
                                border-bottom: 1px solid black;\
                                background-color: steelblue;\
                                color: white;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: steelblue}')
        elif option == 'White-Square-Table':  # White BG, Square Bottom Border For Tables
            self.setStyleSheet('QPushButton{\
                                border-top: 0px solid black;\
                                border-left: 0px solid black;\
                                border-right: 0px solid black;\
                                border-bottom: 1px solid black;\
                                background-color: white;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: steelblue;\
                                color: white}\
                                QPushButton:pressed{\
                                background-color: dodgerblue;\
                                color: white}')
        elif option == 'White-Square':  # White BG, Square Border
            self.setStyleSheet('QPushButton{\
                                    border: 1px solid black;\
                                    background-color: white;\
                                    color: black;\
                                    padding: 2px}\
                                    QPushButton:hover{\
                                    background-color: lightgray}\
                                    QPushButton:pressed{\
                                    border: 1px solid steelblue}')
        elif option == 'Gray-Square':  # Gray BG, Square Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                background-color: lightgray;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 2px solid white}\
                                QPushButton:pressed{\
                                border: 3px solid white}')
        elif option == 'Light-Gray-Square':  # Light Gray BG, Square Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                background-color: rgb(243, 243, 243);\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 2px solid white}\
                                QPushButton:pressed{\
                                border: 3px solid white}')
        elif option == 'Blue-Square':  # Blue BG, Square Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                background-color: steelblue;\
                                color: white;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 1px solid dodgerblue}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')
        elif option == 'White-Round':  # White BG, Rounded Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                border-radius: 6;\
                                background-color: white;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                background-color: lightgray}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')
        elif option == 'White-None':  # White BG, No Border
            self.setStyleSheet('QPushButton{\
                                border: 0px solid black;\
                                background-color: white;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 1px solid dodgerblue}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')
        elif option == 'Blue-Round':  # Blue BG, Rounded Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                border-radius: 6;\
                                background-color: steelblue;\
                                color: rgb(230, 230, 230);\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 1px solid dodgerblue}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')
        elif option == 'Green-Round':  # Green BG, Rounded Border
            self.setStyleSheet('border: 1px solid black;\
                                border-radius: 6;\
                                background-color: green;\
                                color: white;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 1px solid dodgerblue}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')
        elif option == 'Red-Round':  # Red BG, Rounded Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                border-radius: 6;\
                                background-color: tomato;\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 1px solid dodgerblue}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')
        elif option == 'LightGray-Round':  # Light Gray BG, Rounded Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                border-radius: 6;\
                                background:rgb(243, 243, 243);\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 1px solid dodgerblue}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')
        elif option == 'MediumGray-Round':  # Medium Gray BG, Rounded Border
            self.setStyleSheet('QPushButton{\
                                border: 1px solid black;\
                                border-radius: 6;\
                                background:rgb(213, 213, 213);\
                                color: black;\
                                padding: 2px}\
                                QPushButton:hover{\
                                border: 1px solid dodgerblue}\
                                QPushButton:pressed{\
                                border: 1px solid steelblue}')


class clsMachine:
    def __init__(self, main, machine, x, y, orientation, selectedBlueprint, starterQuantity=1, filterLeft=None,
                 filterRight=None, teleportID=None, filterArm=None):
        # Machine variables
        self.main = main
        self.type = machine  # Machine type
        self.x = x  # Machine position
        self.y = y  # Machine position
        self.orientation = orientation  # Machine orientation
        self.cost = self.main.machineLib.lib[self.type]['buildCost']  # Tool cost
        self.value = int(self.main.machineLib.lib[self.type]['buildCost'] / 4)  # Sell back value is 25% of cost
        self.op_cost = self.main.machineLib.lib[self.type]['opCost']  # Tool operation cost
        self.op_time = self.main.machineLib.lib[self.type]['opTime']  # Tool operation time
        self.queueDelay = 0  # Delay to spawn queued material
        self.queueMaterial = None  # Queued material
        self.assyLine = self.getAssyLineNumber()  # Assembly line number of tool
        self.consideredBlueprints = []  # Blueprints considered
        self.contains = {}  # Machine inventory
        self.onFloor = False  # Flag - Material on floor
        self.starterQuantity = starterQuantity  # Starter - Spawn quantity
        self.selectedBlueprint = selectedBlueprint  # Starter, Crafter - Blueprint selected
        self.splitOutput = [0, 0, 0]  # Splitter - Iteration split distribution
        self.splitCumulative = [0, 0, 0]  # Splitter - Cumulative split counter
        self.splitSetting = None   # Splitter - Split setting
        self.splitTurn = 0  # Splitter - Split turn
        self.filterLeft = filterLeft  # Filter - Material selection left
        self.filterRight = filterRight  # Filter - Material selection right
        self.filterArm = filterArm  # Filter - Material selection arm
        self.motionInProgress = False  # Robotic Arm - Motion in progress flag
        self.motionFrame = 1  # Robotic Arm - Current motion frame number
        self.returnMotion = False  # Robotic Arm - Motion direction flag
        self.heldMaterial = None  # Robotic Arm - Held material object
        self.xPickUpZone = None  # Robotic Arm - Material pick up zone x
        self.yPickUpZone = None  # Robotic Arm - Material pick up zone y
        self.xDropOffZone = None  # Robotic Arm - Material drop off zone x
        self.yDropOffZone = None  # Robotic Arm - Material drop off zone y
        self.xAbsLinkCenterAB = None  # Robotic Arm - Link Center
        self.yAbsLinkCenterAB = None  # Robotic Arm - Link Center
        self.xAbsLinkCenterBC = None  # Robotic Arm - Link Center
        self.yAbsLinkCenterBC = None  # Robotic Arm - Link Center
        self.teleporterID = teleportID  # Teleporter - ID number
        self.teleporterActivated = False  # Teleporter - Activation (Unique ID Pairing)

        # Machine image and shape setup
        self.shapeTop = None  # Shape Object - Top of Machine
        self.shapeBottom = None  # Shape Object - Bottom of Machine
        self.shapeImageTop = None  # Image Address - Top of Machine
        self.shapeImageBottom = None  # Image Address - Bottom of Machine
        self.shapeArm1 = None  # Shape Object - Robotic Arm Link 1
        self.shapeArm2 = None  # Shape Object - Robotic Arm Link 2
        self.xShape = None  # Machine Center x and y in scene coords
        self.yShape = None  # Machine Center x and y in scene coords
        self.arrow = None

        self.machineTypeSpecificSetup()

        self.drawShape()

    # -------- Machine Type Specific Setup -------- #

    def machineTypeSpecificSetup(self):
        if self.type in [STARTER, CRAFTER]:  # Only consider selected blueprint by menu
            if self.selectedBlueprint is not None:
                self.consideredBlueprints.append(self.selectedBlueprint)

        elif self.type in [DRAWER, CUTTER, FURNACE, PRESS]:  # Consider all its blueprints in its lib def
            self.consideredBlueprints.extend(self.main.machineBlueprintList[self.type])  # Add pre-computed list

        elif self.type in [SELLER, ROLLER]:
            pass

        elif self.type in [SPLITTER_LEFT, SPLITTER_RIGHT, SPLITTER_TEE, SPLITTER_3WAY]:
            if self.type == SPLITTER_3WAY:  # <^>
                self.splitSetting = [1, 1, 1]  # Split settings - Relative Left, Straight, Right
            elif self.type == SPLITTER_TEE:  # <_>
                self.splitSetting = [1, 0, 1]  # Split settings - Relative Left, Straight, Right
            elif self.type == SPLITTER_LEFT:  # <^_
                self.splitSetting = [1, 1, 0]  # Split settings - Relative Left, Straight, Right
            elif self.type == SPLITTER_RIGHT:  # _^>
                self.splitSetting = [0, 1, 1]  # Split settings - Relative Left, Straight, Right

        elif self.type in [FILTER_LEFT, FILTER_RIGHT, FILTER_TEE]:
            pass

        elif self.type in [TELEPORTER_INPUT]:
            pass

        elif self.type in [TELEPORTER_OUTPUT]:
            pass

        elif self.type in [ROBOTIC_ARM, FILTERED_ARM]:
            self.setPickupDropOffZones()
            self.setUpdatedArmPositions()  # Update arm pos parameters

    # -------- Splitter Methods -------- #

    def splitMaterial(self, piece):
        if self.splitSetting[self.splitTurn] == 0:  # Only 1 direction should be zero for any splitter
            self.splitTurn = (self.splitTurn + 1) % 3

        self.splitOutput = [0, 0, 0]  # Initialize output queue to zeros [L, S, R]
        for i in range(0, piece.quantity):
            self.splitOutput[self.splitTurn] += 1  # Allocate 1 piece to output Queue in current direction
            self.splitCumulative[self.splitTurn] += 1  # Allocate 1 piece to cumulative count in current direction
            if self.splitCumulative[self.splitTurn] >= self.splitSetting[self.splitTurn]:  # Wait to hit cap then rotate
                self.splitCumulative[self.splitTurn] = 0
                self.splitTurn = (self.splitTurn + 1) % 3

        orientationIndex = ORIENTATIONS.index(self.orientation)  # [U, L, D, R]
        if self.splitOutput[0] > 0:
            self.main.Materials.append(clsMaterial(
                self.main, piece.type, self.x, self.y, ORIENTATIONS[(orientationIndex + 3) % 4],
                self.splitOutput[0]))  # Left
        if self.splitOutput[1] > 0:
            self.main.Materials.append(clsMaterial(
                self.main, piece.type, self.x, self.y, ORIENTATIONS[(orientationIndex + 0) % 4],
                self.splitOutput[1]))  # Straight
        if self.splitOutput[2] > 0:
            self.main.Materials.append(clsMaterial(
                self.main, piece.type, self.x, self.y, ORIENTATIONS[(orientationIndex + 1) % 4],
                self.splitOutput[2]))  # Right
        piece.delMaterial()

    # -------- Filter Methods -------- #

    def filterMaterial(self, material):
        orientationIndex = ORIENTATIONS.index(self.orientation)  # [U, L, D, R]
        if material.type == self.filterLeft:
            material.orientation = ORIENTATIONS[(orientationIndex + 3) % 4]  # Set to Left
        elif material.type == self.filterRight:
            material.orientation = ORIENTATIONS[(orientationIndex + 1) % 4]  # Set to Right

    # -------- Teleporter Methods -------- #

    def teleportMaterial(self, material):
        for tool in self.main.Machines:
            if tool.type == TELEPORTER_OUTPUT and tool.teleporterID == self.teleporterID:
                material.x = tool.x
                material.y = tool.y
                material.orientation = tool.orientation
                material.drawShape()
                return
        self.main.updateMessage('Material destroyed by teleporter')
        material.delMaterial()  # Del mat if no matching teleporter

    # -------- Robotic Arm Methods -------- #

    def setPickupDropOffZones(self):
        if self.orientation == 'U':
            self.xPickUpZone, self.yPickUpZone = self.x, self.y - GRID_SIZE
            self.xDropOffZone, self.yDropOffZone = self.x, self.y + GRID_SIZE
        elif self.orientation == 'D':
            self.xPickUpZone, self.yPickUpZone = self.x, self.y + GRID_SIZE
            self.xDropOffZone, self.yDropOffZone = self.x, self.y - GRID_SIZE
        elif self.orientation == 'L':
            self.xPickUpZone, self.yPickUpZone = self.x + GRID_SIZE, self.y
            self.xDropOffZone, self.yDropOffZone = self.x - GRID_SIZE, self.y
        elif self.orientation == 'R':
            self.xPickUpZone, self.yPickUpZone = self.x - GRID_SIZE, self.y
            self.xDropOffZone, self.yDropOffZone = self.x + GRID_SIZE, self.y

    def pickUpMaterial(self, material):
        if self.type == ROBOTIC_ARM or (self.type == FILTERED_ARM and material.type == self.filterArm):
            if material.quantity > 1:
                material.quantity -= 1  # Arm only picks up quantity one of a multiple quantity stack
                material.setMaterialImage()  # Update material image to match new quantity
                material.drawShape()  # Redraw material shape
                newMaterial = clsMaterial(material.main, material.type, material.x, material.y, material.orientation, 1)
                self.main.Materials.append(newMaterial)
                self.heldMaterial = newMaterial
            else:
                self.heldMaterial = material
            self.motionInProgress = True
            self.motionFrame = 1
            self.heldMaterial.pickedUp = True
            self.heldMaterial.shape.setZValue(Z_PICKED_UP)

    def dropOffMaterial(self):
        self.heldMaterial.x = self.xDropOffZone
        self.heldMaterial.y = self.yDropOffZone - 1  # Drop material 1px below tile center so it moves to center next
        self.heldMaterial.orientation = 'U'  # Set orientation to up so it moves onto tile center next
        self.heldMaterial.shape.setZValue(Z_MATERIAL)
        self.heldMaterial.drawShape()
        self.heldMaterial.pickedUp = False
        self.heldMaterial = None
        self.returnMotion = True  # Trigger backwards motion animation

    def getAssyLineNumber(self):
        if 0 <= self.x <= 16 * GRID_SIZE:  # Row 1 thru 16 valid
            return 1
        elif 17 * GRID_SIZE <= self.x <= 35 * GRID_SIZE:  # Row 18 thru 34 valid
            return 2
        elif 36 * GRID_SIZE <= self.x <= 53 * GRID_SIZE:  # Row 36 thru 52 valid
            return 3

    def setSelectedBlueprint(self, material):  # Only for Starter and Crafter have blueprint select option
        self.selectedBlueprint = material
        self.consideredBlueprints.clear()
        self.consideredBlueprints.append(self.selectedBlueprint)

    def addMaterialToInventory(self, material):
        for i in range(material.quantity):  # Accounts for stacks of material
            self.contains[material.type] = self.contains.get(material.type, 0) + 1  # Default to 0 if none then add 1

    def clearInventory(self):
        self.contains.clear()

    def moveMachine(self, x, y):
        self.x = x
        self.y = y
        if self.type in [ROBOTIC_ARM, FILTERED_ARM]:
            self.motionInProgress = False
            self.motionFrame = 1
            self.setUpdatedArmPositions()
            self.setPickupDropOffZones()
            self.setUpdatedArmPositions()  # Update arm pos parameters
            if self.heldMaterial is not None:
                self.heldMaterial.delMaterial()
                self.heldMaterial = None
        self.drawShape()  # Update robotic arm positions before drawShape

    def rotateMachine(self):
        orientationIndex = ORIENTATIONS.index(self.orientation)
        newOrientationIndex = (orientationIndex + 1) % 4  # [U, L, D, R]
        self.orientation = ORIENTATIONS[newOrientationIndex]
        self.setPickupDropOffZones()  # Update pickup/dropoff zone parameters
        self.setUpdatedArmPositions()  # Update arm pos parameters
        self.drawShape()
        self.drawArrow()  # Redraw the arrow on top

    def sellMachine(self):
        self.main.updateBalance(self.main.balance + self.value)
        self.main.updateMessage('Sold Machine for $%s' % self.main.shortNum(self.value))
        self.delMachine()

    def delMachine(self):
        self.delArrow()
        self.delShape()
        self.main.Machines.remove(self)  # Don't del object, remove from list and let garb collect

    def drawShape(self):
        pixmap = self.main.machineLib.lib[self.type]['imageBottom']
        if self.shapeBottom is None:
            self.shapeBottom = self.addShapeToScene(pixmap, Z_MACHINE_BOTTOM, rotate=True)
        self.setShapePosAndPixmap(self.shapeBottom, self.x, self.y, pixmap)
        self.shapeBottom.setRotation(ANGLE[self.orientation])

        pixmap = self.main.machineLib.lib[self.type]['imageTop']
        if self.shapeTop is None:
            self.shapeTop = self.addShapeToScene(pixmap, Z_MACHINE_TOP, rotate=True)
        self.setShapePosAndPixmap(self.shapeTop, self.x, self.y, pixmap)
        self.shapeTop.setRotation(ANGLE[self.orientation])

        if self.type in [ROBOTIC_ARM, FILTERED_ARM]:  # Arms shouldn't rotate real-time, setPixmap to rotated version
            pixmap = self.main.angledPixmapLink1[self.main.thetaAB[self.orientation][self.motionFrame]]
            if self.shapeArm1 is None:
                self.shapeArm1 = self.addShapeToScene(pixmap, Z_ROBOT_ARM, rotate=False)
            self.setShapePosAndPixmap(self.shapeArm1, self.xAbsLinkCenterAB, self.yAbsLinkCenterAB, pixmap)

            pixmap = self.main.angledPixmapLink2[self.main.thetaBC[self.orientation][self.motionFrame]]
            if self.shapeArm2 is None:
                self.shapeArm2 = self.addShapeToScene(pixmap, Z_ROBOT_ARM, rotate=False)
            self.setShapePosAndPixmap(self.shapeArm2, self.xAbsLinkCenterBC, self.yAbsLinkCenterBC, pixmap)

    def addShapeToScene(self, pixmap, zValue, rotate):
        newShape = self.main.scene.addPixmap(pixmap)
        if rotate is True:
            newShape.setTransformOriginPoint(MACHINE_SIZE / 2, MACHINE_SIZE / 2)  # Set rotation around pixmap center
        newShape.setZValue(zValue)
        return newShape

    def setShapePosAndPixmap(self, shape, x, y, pixmap):
        xShape, yShape = self.main.convertToSceneCoords(x, y, pixmap.width(), pixmap.height())
        shape.setPos(xShape, yShape)
        shape.setPixmap(pixmap)

    def processArmMovement(self):
        if self.motionInProgress is True:
            # Display next gif frame
            self.setUpdatedArmPositions()
            self.setShapePosAndPixmap(self.shapeArm1, self.xAbsLinkCenterAB, self.yAbsLinkCenterAB,
                                      self.main.angledPixmapLink1[
                                          self.main.thetaAB[self.orientation][self.motionFrame]])
            self.setShapePosAndPixmap(self.shapeArm2, self.xAbsLinkCenterBC, self.yAbsLinkCenterBC,
                                      self.main.angledPixmapLink2[
                                          self.main.thetaBC[self.orientation][self.motionFrame]])
            self.moveMaterialHeldByArm()

            # Set material down and start return animation
            if self.motionFrame == 48:  # Robotic Arm should have 48 frames
                self.dropOffMaterial()

            # Mark end of animation
            if self.returnMotion is True and self.motionFrame == 1:
                self.motionInProgress = False
                self.returnMotion = False

            # Increment motionFrame frame counter
            if self.motionInProgress is True and self.returnMotion is False:
                self.motionFrame += 1
            elif self.motionInProgress is True and self.returnMotion is True:
                self.motionFrame -= 1

    def setUpdatedArmPositions(self):
        self.xAbsLinkCenterAB = self.x + self.main.xRelLinkCenterAB[self.orientation][self.motionFrame]
        self.yAbsLinkCenterAB = self.y + self.main.yRelLinkCenterAB[self.orientation][self.motionFrame]

        self.xAbsLinkCenterBC = self.x + self.main.xRelLinkCenterBC[self.orientation][self.motionFrame]
        self.yAbsLinkCenterBC = self.y + self.main.yRelLinkCenterBC[self.orientation][self.motionFrame]

    def moveMaterialHeldByArm(self):
        if self.heldMaterial is not None:
            self.heldMaterial.move(self.x + self.main.xRelC[self.orientation][self.motionFrame],
                                   self.y + self.main.yRelC[self.orientation][self.motionFrame])

    def delShape(self):
        if self.shapeTop is not None:
            self.main.scene.removeItem(self.shapeTop)
            self.shapeTop = None
        if self.shapeBottom is not None:
            self.main.scene.removeItem(self.shapeBottom)
            self.shapeBottom = None
        if self.shapeArm1 is not None:
            self.main.scene.removeItem(self.shapeArm1)
            self.shapeArm1 = None
        if self.shapeArm2 is not None:
            self.main.scene.removeItem(self.shapeArm2)
            self.shapeArm2 = None

    def drawArrow(self):
        # Define arrow path in space
        path = QtGui.QPainterPath()
        path.moveTo(0, 8)  # Straight Line
        path.lineTo(0, -8)
        path.moveTo(0, 8)  # Diagonal to Left
        path.lineTo(-6, 2)
        path.moveTo(0, 8)  # Diagonal to Right
        path.lineTo(6, 2)

        # Add arrow to scene, set position, set rotation
        self.delArrow()
        self.xShape, self.yShape = self.main.convertToSceneCoords(self.x, self.y, 0, 0)
        self.arrow = self.main.scene.addPath(path, QtGui.QPen(QtCore.Qt.red, 2))
        self.arrow.setPos(self.xShape, self.yShape)
        self.arrow.setZValue(Z_ARROW)
        self.arrow.setRotation(ANGLE[self.orientation])

    def delArrow(self):
        if self.arrow is not None:
            self.main.scene.removeItem(self.arrow)
            self.arrow = None


class clsMaterial:
    def __init__(self, main, materialType, x, y, orientation, quantity):
        self.main = main
        self.type = materialType
        self.x = x  # Material x position
        self.y = y  # Material y position
        self.orientation = orientation  # Material orientation
        self.quantity = quantity  # Quantity of material in stack (1, 2, or 3)
        self.value = self.main.materialLib.lib[self.type]['value']  # Material sale price
        self.pickedUp = False  # Flag material picked up by Robotic Arm
        self.group = None  # Material group (Reference to an unnamed shared list of materials in a group)
        self.groupPos = None  # Position in the material group
        self.xVisOffset = 0  # Visual x offset on rollers
        self.yVisOffset = 0  # Visual y offset on rollers
        self.image = None

        # Material Shape Setup
        self.xShape = None
        self.yShape = None
        self.shape = None
        self.setMaterialImage()
        self.shapeImage = None
        self.drawShape()

    def setMaterialImage(self):
        if self.quantity == 1:
            self.image = self.main.materialLib.lib[self.type]['image']
        elif self.quantity == 2:
            self.image = self.main.materialLib.lib[self.type]['image_qty_2']
        elif self.quantity == 3:
            self.image = self.main.materialLib.lib[self.type]['image_qty_3']

    def rollerMove(self):  # Move forward 1px by orientation
        i = ORIENTATIONS.index(self.orientation)  # [U, L, D, R]
        xMovement = [0, -1, 0, 1]
        yMovement = [1, 0, -1, 0]
        self.x += xMovement[i]
        self.y += yMovement[i]
        self.xShape, self.yShape = self.main.convertToSceneCoords(self.x + self.xVisOffset, self.y + self.yVisOffset,
                                                                  MAT_SIZE, MAT_SIZE)
        self.shape.setPos(self.xShape, self.yShape)

    def move(self, xNew, yNew):  # Move material to given location
        self.x = xNew
        self.y = yNew
        self.xShape, self.yShape = self.main.convertToSceneCoords(self.x + self.xVisOffset, self.y + self.yVisOffset,
                                                                  MAT_SIZE, MAT_SIZE)
        self.shape.setPos(self.xShape, self.yShape)

    def checkIfAtTileCenter(self):
        # This method may or may not be faster. Need to do a speed test to find out if it is.
        # This code runs once in main application
        #   xTileCenters = range(13, self.main.sceneWidth, GRID_SIZE)
        #   yTileCenters = range(13, self.main.sceneHeight, GRID_SIZE)
        # This function changes to simple check if x and y are in the list of centers
        #   if self.x in xTileCenters and self.y in yTileCenters
        #       return True
        #   else:
        #       return False

        if (self.x - 13) % GRID_SIZE == 0 and (self.y - 13) % GRID_SIZE == 0:
            return True
        else:
            return False

    def setGroupVisualOffset(self, offsetList):
        self.xVisOffset, self.yVisOffset = offsetList[self.groupPos % 9]  # Mod 9 to restart positioning after 9

    def delMaterial(self):
        if self.group is not None:
            self.group.remove(self)  # Remove material from group
        self.delShape()
        self.main.Materials.remove(self)

    def drawShape(self):
        self.delShape()
        self.xShape, self.yShape = self.main.convertToSceneCoords(self.x + self.xVisOffset, self.y + self.yVisOffset,
                                                                  MAT_SIZE, MAT_SIZE)
        self.shape = self.main.scene.addPixmap(self.image)
        self.shape.setZValue(Z_MATERIAL)
        self.shape.setPos(self.xShape, self.yShape)

    def delShape(self):
        if self.shape is not None:
            self.main.scene.removeItem(self.shape)
            self.shape = None


class clsTile:
    def __init__(self, main, x, y):
        self.main = main
        self.x = x
        self.y = y
        self.assyLine = self.getAssyLineNumber()
        self.locked = False
        self.walled = False
        self.shape_highlight = None
        self.shape_lock = None
        self.shape_wall = None
        self.xShape = None
        self.yShape = None
        self.xShape = self.x
        self.yShape = self.main.sceneHeight - self.y  # Scene and material coord system differ

    def getAssyLineNumber(self):
        if 0 <= self.x <= 16 * GRID_SIZE:  # Row 1 thru 16 valid
            return 1
        elif 17 * GRID_SIZE <= self.x <= 35 * GRID_SIZE:  # Row 18 thru 34 valid
            return 2
        elif 36 * GRID_SIZE <= self.x <= 53 * GRID_SIZE:  # Row 36 thru 52 valid
            return 3

    def buyTile(self):
        self.markAsUnlocked()
        self.main.updateBalance(self.main.balance - self.main.getTilePrice())
        self.main.updateMessage('Bought Tile for $%s!' % self.main.shortNum(self.main.getTilePrice()))
        self.main.unlockedTiles.append((self.x, self.y))
        self.main.statusBar.showMessage('Purchase a Tile for $%s' % self.main.shortNum(self.main.getTilePrice()))

    def markAsLocked(self):
        self.drawShape(LOCK)
        self.locked = True

    def markAsUnlocked(self):
        self.delShape(LOCK)
        self.locked = False

    def markAsWalled(self):
        self.drawShape(WALL)
        self.walled = True

    def markAsUnwalled(self):
        self.delShape(WALL)
        self.walled = False

    def markAsHighlighted(self):
        self.drawShape(HIGHLIGHT)

    def markAsNotHighlighted(self):
        self.delShape(HIGHLIGHT)

    def drawShape(self, shapeType):
        self.delShape(shapeType)
        if shapeType == HIGHLIGHT:
            self.xShape, self.yShape = self.main.convertToSceneCoords(self.x, self.y, GRID_SIZE, GRID_SIZE)
            self.shape_highlight = QtWidgets.QGraphicsRectItem(
                QtCore.QRectF(self.xShape, self.yShape, GRID_SIZE, GRID_SIZE))
            self.shape_highlight.setZValue(Z_HIGHLIGHT)
            self.shape_highlight.setPen(QtGui.QPen(QtCore.Qt.green, 3))
            self.main.scene.addItem(self.shape_highlight)
        elif shapeType == LOCK:
            self.xShape, self.yShape = self.main.convertToSceneCoords(self.x, self.y, MACHINE_SIZE, MACHINE_SIZE)
            self.shape_lock = QtWidgets.QGraphicsRectItem(
                QtCore.QRectF(self.xShape, self.yShape, MACHINE_SIZE, MACHINE_SIZE))
            self.shape_lock.setZValue(Z_HIGHLIGHT)
            self.shape_lock.setBrush(QtGui.QColor(200, 200, 200))
            self.shape_lock.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            self.main.scene.addItem(self.shape_lock)
        elif shapeType == WALL:
            pixmap = self.main.imageLib.lib['Wall']['image']
            self.xShape, self.yShape = self.main.convertToSceneCoords(self.x, self.y, pixmap.width(), pixmap.height())
            self.shape_wall = self.main.scene.addPixmap(pixmap)
            self.shape_wall.setZValue(Z_HIGHLIGHT)
            self.shape_wall.setPos(self.xShape, self.yShape)

    def delShape(self, shapeType):
        if shapeType == HIGHLIGHT:
            if self.shape_highlight is not None:
                self.main.scene.removeItem(self.shape_highlight)
                self.shape_highlight = None
        elif shapeType == LOCK:
            if self.shape_lock is not None:
                self.main.scene.removeItem(self.shape_lock)
                self.shape_lock = None
        elif shapeType == WALL:
            if self.shape_wall is not None:
                self.main.scene.removeItem(self.shape_wall)
                self.shape_wall = None


# noinspection PyArgumentList,PyArgumentList,PyUnresolvedReferences
class baseMenuFrame(QtWidgets.QFrame):
    # Menu Frame GUI Setup
    # BaseMenuFrame (QFrame) [vbox (QVBox)]
    #     topW
    #     grid
    #     bottomW

    def __init__(self, parent=None, main=None):
        super(baseMenuFrame, self).__init__(parent)
        self.parent = parent
        self.main = main
        self.setMinimumWidth(480)
        self.setMinimumHeight(600)

        # Frame Setup
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setObjectName('baseMenuFrame')
        self.setStyleSheet('#baseMenuFrame{background-color: white;\
                           border: 1px solid black}')

        # Top Bar
        self.topW = QtWidgets.QFrame()
        topWLayout = QtWidgets.QVBoxLayout()
        self.topW.setMinimumHeight(65)
        self.topW.setObjectName('baseMenuFrameTop')
        self.topW.setStyleSheet('#baseMenuFrameTop{background:rgb(243, 243, 243);\
                                 border-top: 0px solid black;\
                                 border-left: 0px solid black;\
                                 border-right: 0px solid black;\
                                 border-bottom: 1px solid black;\
                                 color: black}')
        self.titleL = QLabelT('Title')
        topWLayout.setContentsMargins(0, 0, 0, 0)
        topWLayout.addWidget(self.titleL)
        self.topW.setLayout(topWLayout)

        # Bottom Bar
        self.bottomW = QtWidgets.QFrame()
        bottomWLayout = QtWidgets.QVBoxLayout()
        self.bottomW.setMinimumHeight(50)
        self.bottomW.setObjectName('baseMenuFrameBottom')
        self.bottomW.setStyleSheet('#baseMenuFrameBottom{background:rgb(243, 243, 243);\
                                    border-top: 1px solid black;\
                                    border-left: 0px solid black;\
                                    border-right: 0px solid black;\
                                    border-bottom: 0px solid black;\
                                    color: black}')
        self.cancelB = QPushButtonA('Cancel', 'White-Square', 200)
        self.cancelB.clicked.connect(lambda: self.main.closeMode())
        bottomWLayout.setAlignment(QtCore.Qt.AlignCenter)
        bottomWLayout.addWidget(self.cancelB)
        self.bottomW.setLayout(bottomWLayout)

        # Grid Contents - Subclass adds content to this layout
        self.contents = QtWidgets.QWidget()

        # Frame's Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.topW)
        vbox.addStretch(1)
        vbox.addWidget(self.contents)
        vbox.addStretch(1)
        vbox.addWidget(self.bottomW)
        self.setLayout(vbox)


# noinspection PyArgumentList,PyArgumentList
class scrollingBaseMenuFrame(QtWidgets.QFrame):
    # Scrolling Menu Frame GUI Setup
    # scrollingBaseMenuFrame (QFrame) [QVBox]
    #     scrollArea (QScrollArea)
    #         scrollAreaWidgetContents (QWidget) [QVBox] (Scrolling)
    #             topW
    #             grid
    #     bottomW (Static)

    def __init__(self, parent=None, main=None):
        super(scrollingBaseMenuFrame, self).__init__(parent)
        self.parent = parent
        self.main = main
        self.setMinimumWidth(500)
        self.setMinimumHeight(480)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Frame Setup
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setObjectName('baseMenuFrame')
        self.setStyleSheet('#baseMenuFrame{\
                            background-color: white;\
                            border: 1px solid black}')

        # Top Bar
        self.topW = QtWidgets.QFrame()
        topWLayout = QtWidgets.QVBoxLayout()
        self.topW.setMinimumHeight(65)
        self.topW.setObjectName('baseMenuFrameTop')
        self.topW.setStyleSheet('#baseMenuFrameTop{background:rgb(243, 243, 243);\
                                 border-top: 0px solid black;\
                                 border-left: 0px solid black;\
                                 border-right: 0px solid black;\
                                 border-bottom: 1px solid black;\
                                 color: black}')
        self.titleL = QLabelT('Title')
        topWLayout.setContentsMargins(0, 0, 0, 0)
        topWLayout.addWidget(self.titleL)
        self.topW.setLayout(topWLayout)

        # Bottom Bar
        self.bottomW = QtWidgets.QFrame()
        bottomWLayout = QtWidgets.QVBoxLayout()
        self.bottomW.setMinimumHeight(50)
        self.bottomW.setObjectName('baseMenuFrameBottom')
        self.bottomW.setStyleSheet('#baseMenuFrameBottom{\
                                    background:rgb(243, 243, 243);\
                                    border-top: 1px solid black;\
                                    border-left: 0px solid black;\
                                    border-right: 0px solid black;\
                                    border-bottom: 0px solid black;\
                                    color: black}')
        self.cancelB = QPushButtonA('Cancel', 'White-Square', 200)
        bottomWLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.cancelB.clicked.connect(lambda: self.main.closeMode())
        bottomWLayout.addWidget(self.cancelB)
        self.bottomW.setLayout(bottomWLayout)

        # Grid Contents
        self.contents = QtWidgets.QWidget()

        # Scrolling Contents Setup
        self.scrollAreaWidgetContents = QtWidgets.QWidget()  # Scroll Area Contents Wid
        self.scrollAreaWidgetContents.setObjectName('baseMenuScrollingContents')
        self.scrollAreaWidgetContents.setStyleSheet('#baseMenuScrollingContents{\
                                                    background-color: white;\
                                                    border-top: 0px solid black;\
                                                    border-left: 0px solid black;\
                                                    border-right: 0px solid black;\
                                                    border-bottom: 0px solid black;}')
        vbox = QtWidgets.QVBoxLayout()  # Top level layout
        vbox.addWidget(self.topW)
        vbox.addWidget(self.contents)
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaWidgetContents.setLayout(vbox)

        # Scrolling Layout
        self.scrollArea = QtWidgets.QScrollArea()  # Add ScrollArea to self
        self.scrollArea.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)  # Set Scroll Area to Contents Wid
        self.scrollArea.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollArea)
        layout.addWidget(self.bottomW)
        self.setLayout(layout)


# noinspection PyArgumentList,PyArgumentList,PyArgumentList,PyUnresolvedReferences
class toolPropertiesMenu(baseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(toolPropertiesMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMaximumHeight(700)
        self.titleL.setText('None')

        # Set Contents
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)

        # Blueprint Layout
        self.blueprintWidget = QtWidgets.QFrame()
        self.blueprintWidget.setObjectName('blueprintWidget')
        self.blueprintWidget.setStyleSheet('#blueprintWidget{background-color: rgb(243, 243, 243);\
                                           margin:20px;\
                                           border:1px solid black;}')
        self.blueprintWidget.setFixedHeight(280)
        self.blueprintSubGrid = QtWidgets.QGridLayout()
        self.blueprintSubGrid.setSpacing(14)
        self.blueprintSubGrid.setContentsMargins(8, 8, 8, 8)

        self.curBlueprintL = QLabelA('Blueprint', 'Light-Gray-None', None, 13)

        self.itemFrame = QtWidgets.QFrame()
        self.itemFrame.setStyleSheet('QFrame{\
                                     background-color:\
                                     gray; border: 1px solid black}')
        self.itemGrid = QtWidgets.QGridLayout()
        self.itemGrid.setAlignment(QtCore.Qt.AlignLeft)

        self.blankImg = QtGui.QPixmap()
        self.baseName = QLabelA('', 'Blue-None', None, 11)
        self.baseImg = QLabelImgA('', self.blankImg, 'Blue-None')
        self.baseQty = QLabelA('', 'Blue-None', None, 11)
        self.baseName.setWordWrap(True)

        self.cellFrame = QtWidgets.QFrame()
        self.cellFrame.setStyleSheet('background-color: steelblue;\
                                      border-radius: 6')
        self.cellFrame.setFixedSize(100, 120)
        cellVBox = QtWidgets.QVBoxLayout()
        cellVBox.setContentsMargins(0, 0, 0, 0)
        cellVBox.addWidget(self.baseName)
        cellVBox.addWidget(self.baseImg)
        cellVBox.addWidget(self.baseQty)
        self.cellFrame.setLayout(cellVBox)
        self.cellFrame.setContentsMargins(2, 2, 2, 2)

        self.itemGrid.addWidget(self.cellFrame, 1, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.componentName = {}
        self.componentImg = {}
        self.componentQty = {}

        for j in range(0, 3):
            self.componentName[j] = QLabelA('', 'White-None', None, 11)
            self.componentImg[j] = QLabelImgA('', self.blankImg, 'White-None')
            self.componentQty[j] = QLabelA('', 'White-None', None, 11)
            self.componentName[j].setWordWrap(True)

            self.compcellFrame = QtWidgets.QFrame()
            self.compcellFrame.setStyleSheet('background-color: white;\
                                              border-radius: 6')
            self.compcellFrame.setFixedSize(100, 120)
            cellVBox = QtWidgets.QVBoxLayout()
            cellVBox.setContentsMargins(0, 0, 0, 0)
            cellVBox.addWidget(self.componentName[j])
            cellVBox.addWidget(self.componentImg[j])
            cellVBox.addWidget(self.componentQty[j])
            self.compcellFrame.setLayout(cellVBox)
            self.compcellFrame.setContentsMargins(2, 2, 2, 2)

            self.itemGrid.addWidget(self.compcellFrame, 1, j + 2, 1, 1, QtCore.Qt.AlignCenter)

        self.itemFrame.setLayout(self.itemGrid)

        self.changeBlueprintB = QPushButtonA('Change', 'White-Square', 150)
        self.changeBlueprintB.clicked.connect(lambda: self.main.blueprintSelectFrame.openMenuAndUpdateInfo())

        self.blueprintSubGrid.addWidget(self.curBlueprintL, 1, 1, 1, 3)
        self.blueprintSubGrid.addWidget(self.itemFrame, 2, 1, 1, 3, QtCore.Qt.AlignCenter)
        self.blueprintSubGrid.addWidget(self.changeBlueprintB, 3, 2, 1, 1)
        self.blueprintWidget.setLayout(self.blueprintSubGrid)
        self.vbox.addWidget(self.blueprintWidget)

        # Inventory Layout
        self.inventoryWidget = QtWidgets.QFrame()
        self.inventoryWidget.setObjectName('inventoryWidget')
        self.inventoryWidget.setStyleSheet('#inventoryWidget{background-color: rgb(243, 243, 243);\
                                           margin:20px;\
                                           border:1px solid black;}')
        self.invSubGrid = QtWidgets.QGridLayout()
        self.invSubGrid.setSpacing(14)
        self.invSubGrid.setContentsMargins(8, 8, 8, 24)
        self.invTitleL = QLabelA('Inventory', 'Light-Gray-None', None, 13)

        self.inventoryNameL = {}
        self.inventoryImgL = {}
        self.inventoryQtyL = {}

        for i in range(0, 6):
            self.inventoryNameL[i] = QLabelA('', 'Light-Gray-None', 150)
            self.inventoryImgL[i] = QLabelImgA('', self.blankImg, 'Light-Gray-None', 150)
            self.inventoryQtyL[i] = QLabelA('-', 'Light-Gray-None', 150)

            self.inventoryNameL[i].setFixedHeight(20)
            self.inventoryImgL[i].setFixedHeight(20)
            self.inventoryQtyL[i].setFixedHeight(20)

            self.invSubGrid.addWidget(self.inventoryImgL[i], i + 2, 1)
            self.invSubGrid.addWidget(self.inventoryQtyL[i], i + 2, 2)
            self.invSubGrid.addWidget(self.inventoryNameL[i], i + 2, 3)

        self.clearInvB = QPushButtonA('Clear Inventory', 'White-Square', 150)
        self.clearInvB.clicked.connect(lambda: self.clearInventory())

        self.invSubGrid.addWidget(self.invTitleL, 1, 1, 1, 3)
        self.invSubGrid.addWidget(self.clearInvB, 9, 2)

        self.inventoryWidget.setLayout(self.invSubGrid)
        self.vbox.addWidget(self.inventoryWidget)

        # Qty Layout
        self.qtyWidget = QtWidgets.QFrame()
        self.qtyWidget.setObjectName('qtyWidget')
        self.qtyWidget.setStyleSheet('#qtyWidget{background-color: rgb(243, 243, 243);\
                                           margin:20px;\
                                           border:1px solid black;}')
        self.qtySubGrid = QtWidgets.QGridLayout()
        self.qtySubGrid.setContentsMargins(14, 14, 14, 14)
        self.changeQtyCurrentL = QLabelA('None', 'Light-Gray-None', None, 12)
        self.changeQtyMaxL = QLabelA('None', 'Light-Gray-None', None, 11)
        self.changeQty1B = QPushButtonA('1', 'White-Square', 150)
        self.changeQty2B = QPushButtonA('2', 'White-Square', 150)
        self.changeQty3B = QPushButtonA('3', 'White-Square', 150)

        self.changeQty1B.clicked.connect(lambda: self.setStarterQuantity(1))
        self.changeQty2B.clicked.connect(lambda: self.setStarterQuantity(2))
        self.changeQty3B.clicked.connect(lambda: self.setStarterQuantity(3))

        self.qtySubGrid.addWidget(self.changeQtyCurrentL, 1, 1, 1, 3)
        self.qtySubGrid.addWidget(self.changeQtyMaxL, 2, 1, 1, 3)
        self.qtySubGrid.addWidget(self.changeQty1B, 3, 1, 1, 1)
        self.qtySubGrid.addWidget(self.changeQty2B, 3, 2, 1, 1)
        self.qtySubGrid.addWidget(self.changeQty3B, 3, 3, 1, 1)
        self.qtyWidget.setLayout(self.qtySubGrid)
        self.vbox.addWidget(self.qtyWidget)

        # Splitter Layout
        self.splitWidget = QtWidgets.QFrame()
        self.splitWidget.setObjectName('splitWidget')
        self.splitWidget.setStyleSheet('#splitWidget{background-color: rgb(243, 243, 243);\
                                           margin:20px;\
                                           border:1px solid black;}')
        self.splitSubGrid = QtWidgets.QGridLayout()
        self.splitSubGrid.setContentsMargins(14, 14, 14, 14)

        self.splitLeftL = QLabelA(LEFT, 'Light-Gray-Square')
        self.incLeftB = QPushButtonA('+', 'Light-Gray-Square', 150)
        self.leftL = QLabelA('None', 'Light-Gray-Square')
        self.decLeftB = QPushButtonA('-', 'Light-Gray-Square', 150)

        self.splitStraightL = QLabelA('Straight', 'Light-Gray-Square')
        self.incStraightB = QPushButtonA('+', 'Light-Gray-Square', 150)
        self.straightL = QLabelA('None', 'Light-Gray-Square')
        self.decStraightB = QPushButtonA('-', 'Light-Gray-Square', 150)

        self.splitRightL = QLabelA(RIGHT, 'Light-Gray-Square')
        self.incRightB = QPushButtonA('+', 'Light-Gray-Square', 150)
        self.rightL = QLabelA('None', 'Light-Gray-Square')
        self.decRightB = QPushButtonA('-', 'Light-Gray-Square', 150)

        self.incLeftB.clicked.connect(lambda: self.setSplitSetting(0, 1))
        self.decLeftB.clicked.connect(lambda: self.setSplitSetting(0, -1))
        self.incStraightB.clicked.connect(lambda: self.setSplitSetting(1, 1))
        self.decStraightB.clicked.connect(lambda: self.setSplitSetting(1, -1))
        self.incRightB.clicked.connect(lambda: self.setSplitSetting(2, 1))
        self.decRightB.clicked.connect(lambda: self.setSplitSetting(2, -1))

        self.splitSubGrid.addWidget(self.splitLeftL, 2, 1, 1, 1)
        self.splitSubGrid.addWidget(self.incLeftB, 3, 1, 1, 1)
        self.splitSubGrid.addWidget(self.leftL, 4, 1, 1, 1)
        self.splitSubGrid.addWidget(self.decLeftB, 5, 1, 1, 1)

        self.splitSubGrid.addWidget(self.splitStraightL, 2, 2, 1, 1)
        self.splitSubGrid.addWidget(self.incStraightB, 3, 2, 1, 1)
        self.splitSubGrid.addWidget(self.straightL, 4, 2, 1, 1)
        self.splitSubGrid.addWidget(self.decStraightB, 5, 2, 1, 1)

        self.splitSubGrid.addWidget(self.splitRightL, 2, 3, 1, 1)
        self.splitSubGrid.addWidget(self.incRightB, 3, 3, 1, 1)
        self.splitSubGrid.addWidget(self.rightL, 4, 3, 1, 1)
        self.splitSubGrid.addWidget(self.decRightB, 5, 3, 1, 1)
        self.splitWidget.setLayout(self.splitSubGrid)
        self.vbox.addWidget(self.splitWidget)

        # Filter Layout
        self.filterWidget = QtWidgets.QFrame()
        self.filterWidget.setObjectName('filterWidget')
        self.filterWidget.setStyleSheet('#filterWidget{background-color: rgb(243, 243, 243);\
                                           margin:20px;\
                                           border:1px solid black;}')
        self.filterSubGrid = QtWidgets.QGridLayout()
        self.filterSubGrid.setContentsMargins(14, 14, 14, 14)

        self.filterLeftTitle = QLabelA('Left Filter:', 'Light-Gray-Square')
        self.filterLeftImage = QLabelImgA('', QtGui.QPixmap(''), 'Light-Gray-Square')
        self.filterLeftL = QLabelA('None', 'Light-Gray-Square')
        self.selFilterLeftB = QPushButtonA('Select', 'Light-Gray-Square', 150)

        self.filterRightTitle = QLabelA('Right Filter:', 'Light-Gray-Square')
        self.filterRightImage = QLabelImgA('', QtGui.QPixmap(''), 'Light-Gray-Square')
        self.filterRightL = QLabelA('None', 'Light-Gray-Square')
        self.selFilterRightB = QPushButtonA('Select', 'Light-Gray-Square', 150)

        self.filterSubGrid.addWidget(self.filterLeftTitle, 1, 1, 1, 1)
        self.filterSubGrid.addWidget(self.filterLeftImage, 2, 1, 1, 1)
        self.filterSubGrid.addWidget(self.filterLeftL, 3, 1, 1, 1)
        self.filterSubGrid.addWidget(self.selFilterLeftB, 4, 1, 1, 1)

        self.filterSubGrid.addWidget(self.filterRightTitle, 1, 3, 1, 1)
        self.filterSubGrid.addWidget(self.filterRightImage, 2, 3, 1, 1)
        self.filterSubGrid.addWidget(self.filterRightL, 3, 3, 1, 1)
        self.filterSubGrid.addWidget(self.selFilterRightB, 4, 3, 1, 1)
        self.filterWidget.setLayout(self.filterSubGrid)
        self.vbox.addWidget(self.filterWidget)

        # Filter Arm Layout
        self.filterArmWidget = QtWidgets.QFrame()
        self.filterArmWidget.setObjectName('filterArmWidget')
        self.filterArmWidget.setStyleSheet('#filterArmWidget{background-color: rgb(243, 243, 243);\
                                                  margin:20px;\
                                                  border:1px solid black;}')
        self.filterArmSubGrid = QtWidgets.QGridLayout()
        self.filterArmSubGrid.setContentsMargins(14, 14, 14, 14)

        self.filterArmTitle = QLabelA('Arm Filter:', 'Light-Gray-Square')
        self.filterArmImage = QLabelImgA('', QtGui.QPixmap(''), 'Light-Gray-Square')
        self.filterArmL = QLabelA('None', 'Light-Gray-Square')
        self.selFilterArmB = QPushButtonA('Select', 'Light-Gray-Square', 150)

        self.filterArmSubGrid.addWidget(self.filterArmTitle, 1, 1, 1, 1)
        self.filterArmSubGrid.addWidget(self.filterArmImage, 2, 1, 1, 1)
        self.filterArmSubGrid.addWidget(self.filterArmL, 3, 1, 1, 1)
        self.filterArmSubGrid.addWidget(self.selFilterArmB, 4, 1, 1, 1)
        self.filterArmWidget.setLayout(self.filterArmSubGrid)
        self.vbox.addWidget(self.filterArmWidget)

        # Teleporter Layout
        self.teleportWidget = QtWidgets.QFrame()
        self.teleportWidget.setObjectName('teleportWidget')
        self.teleportWidget.setStyleSheet('#teleportWidget{background-color: rgb(243, 243, 243);\
                                           margin:20px;\
                                           border:1px solid black;}')
        self.teleportSubGrid = QtWidgets.QGridLayout()
        self.teleportSubGrid.setContentsMargins(14, 14, 14, 14)

        self.incB = QPushButtonA('+', 'Light-Gray-Square', 200)
        self.IDNumL = QLabelA('None', 'Light-Gray-Square', 200)
        self.decB = QPushButtonA('-', 'Light-Gray-Square', 200)
        self.TPStatus = QLabelA('None', 'Light-Gray-Square', 200)

        self.incB.clicked.connect(lambda: self.setTeleporterID(1))
        self.decB.clicked.connect(lambda: self.setTeleporterID(-1))

        self.teleportSubGrid.addWidget(self.incB, 1, 2, 1, 1)
        self.teleportSubGrid.addWidget(self.IDNumL, 2, 2, 1, 1)
        self.teleportSubGrid.addWidget(self.decB, 3, 2, 1, 1)
        self.teleportSubGrid.addWidget(self.TPStatus, 4, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.teleportWidget.setLayout(self.teleportSubGrid)
        self.vbox.addWidget(self.teleportWidget)

        # General
        self.contents.setLayout(self.vbox)

        self.blueprintWidget.hide()
        self.inventoryWidget.hide()
        self.qtyWidget.hide()
        self.splitWidget.hide()
        self.filterWidget.hide()
        self.filterArmWidget.hide()
        self.teleportWidget.hide()

    def openMenuAndUpdateInfo(self):
        self.main.openMenu(self)

        # Hide all sub-menus to start then show select few
        self.blueprintWidget.hide()
        self.inventoryWidget.hide()
        self.qtyWidget.hide()
        self.splitWidget.hide()
        self.filterWidget.hide()
        self.filterArmWidget.hide()
        self.teleportWidget.hide()

        self.titleL.setText(self.main.selectedTool.type)

        # Blueprint DisplayInfo
        if self.main.selectedTool.type in [STARTER, CRAFTER]:
            self.blueprintWidget.show()

            # Clears anything there first
            self.baseName.setText('')
            self.baseImg.setPixmap(self.blankImg)
            self.baseQty.setText('')
            for j in range(0, 3):
                self.componentName[j].setText('')
                self.componentImg[j].setPixmap(self.blankImg)
                self.componentQty[j].setText('')

            if self.main.selectedTool.selectedBlueprint is not None:
                self.baseName.setText('%s' % self.main.selectedTool.selectedBlueprint)
                self.baseImg.setPixmap(
                    self.main.materialLib.lib[self.main.selectedTool.selectedBlueprint]['image'].scaled(24, 24))
                self.baseQty.setText('1')

                for j, component in enumerate(
                        self.main.materialLib.lib[self.main.selectedTool.selectedBlueprint]['components']):
                    self.componentName[j].setText('%s' % component)
                    self.componentImg[j].setPixmap(self.main.materialLib.lib[component]['image'].scaled(24, 24))
                    self.componentQty[j].setText(
                        '%s' % self.main.materialLib.lib[
                            self.main.selectedTool.selectedBlueprint]['components'][component])

        # Inventory DisplayInfo
        if self.main.selectedTool.type in [CRAFTER, DRAWER, CUTTER, FURNACE, PRESS]:
            self.inventoryWidget.show()

            # Clear Inventory Listing First
            for i in range(0, len(self.inventoryImgL)):
                self.inventoryImgL[i].setPixmap(self.blankImg)
                self.inventoryQtyL[i].setText('-')
                self.inventoryNameL[i].setText('')

            # Fill Values Based on Inventory
            for i, (key, value) in enumerate(self.main.selectedTool.contains.items()):
                self.inventoryImgL[i].setPixmap(self.main.materialLib.lib[key]['image'].scaled(16, 16))
                self.inventoryQtyL[i].setText(str(value))
                self.inventoryNameL[i].setText(key)

        # Qty DisplayInfo
        if self.main.selectedTool.type in [STARTER]:
            self.qtyWidget.show()
            self.changeQtyMaxL.setText('Max of %s Researched' % self.main.starterMaxSpawnQuantity)
            self.changeQtyCurrentL.setText('Materials Generated Per Operation')
            self.setStarterQuantity(self.main.selectedTool.starterQuantity)  # Sets button marked and enabled status

        # Splitter DisplayInfo
        if self.main.selectedTool.type in [SPLITTER_LEFT, SPLITTER_RIGHT, SPLITTER_TEE, SPLITTER_3WAY]:
            self.splitWidget.show()

            self.leftL.setText(str(self.main.selectedTool.splitSetting[0]))
            self.straightL.setText(str(self.main.selectedTool.splitSetting[1]))
            self.rightL.setText(str(self.main.selectedTool.splitSetting[2]))

            if self.main.selectedTool.type in [SPLITTER_3WAY, SPLITTER_LEFT, SPLITTER_TEE]:
                self.incLeftB.setStyleCode('White-Square')
                self.incLeftB.setEnabled(True)
                self.decLeftB.setStyleCode('White-Square')
                self.decLeftB.setEnabled(True)
            else:
                self.incLeftB.setStyleCode('Gray-Square')
                self.incLeftB.setEnabled(False)
                self.leftL.setText('-')
                self.decLeftB.setStyleCode('Gray-Square')
                self.decLeftB.setEnabled(False)

            if self.main.selectedTool.type in [SPLITTER_3WAY, SPLITTER_LEFT, SPLITTER_RIGHT]:
                self.incStraightB.setStyleCode('White-Square')
                self.incStraightB.setEnabled(True)
                self.decStraightB.setStyleCode('White-Square')
                self.decStraightB.setEnabled(True)
            else:
                self.incStraightB.setStyleCode('Gray-Square')
                self.incStraightB.setEnabled(False)
                self.straightL.setText('-')
                self.decStraightB.setStyleCode('Gray-Square')
                self.decStraightB.setEnabled(False)

            if self.main.selectedTool.type in [SPLITTER_3WAY, SPLITTER_RIGHT, SPLITTER_TEE]:
                self.incRightB.setStyleCode('White-Square')
                self.incRightB.setEnabled(True)
                self.decRightB.setStyleCode('White-Square')
                self.decRightB.setEnabled(True)
            else:
                self.incRightB.setStyleCode('Gray-Square')
                self.incRightB.setEnabled(False)
                self.rightL.setText('-')
                self.decRightB.setStyleCode('Gray-Square')
                self.decRightB.setEnabled(False)

        # Filter DisplayInfo
        if self.main.selectedTool.type in [FILTER_LEFT, FILTER_RIGHT, FILTER_TEE]:
            self.filterWidget.show()
            if self.main.selectedTool.filterLeft is not None:
                self.filterLeftImage.setPixmap(
                    self.main.materialLib.lib[self.main.selectedTool.filterLeft]['image'].scaled(40, 40))
            self.filterLeftL.setText(self.main.selectedTool.filterLeft)
            if self.main.selectedTool.filterRight is not None:
                self.filterRightImage.setPixmap(
                    self.main.materialLib.lib[self.main.selectedTool.filterRight]['image'].scaled(40, 40))
            self.filterRightL.setText(self.main.selectedTool.filterRight)

            self.selFilterLeftB.clicked.connect(lambda: self.main.filterSelectFrame.openMenuAndUpdateInfo(LEFT))
            self.selFilterRightB.clicked.connect(lambda: self.main.filterSelectFrame.openMenuAndUpdateInfo(RIGHT))

            if self.main.selectedTool.type in [FILTER_LEFT, FILTER_TEE]:
                self.selFilterLeftB.setStyleCode('White-Square')
                self.selFilterLeftB.setEnabled(True)
            else:
                self.selFilterLeftB.setStyleCode('Gray-Square')
                self.selFilterLeftB.setEnabled(False)

            if self.main.selectedTool.type in [FILTER_RIGHT, FILTER_TEE]:
                self.selFilterRightB.setStyleCode('White-Square')
                self.selFilterRightB.setEnabled(True)
            else:
                self.selFilterRightB.setStyleCode('Gray-Square')
                self.selFilterRightB.setEnabled(False)

        # Filter Robotic Arm DisplayInfo
        if self.main.selectedTool.type in [FILTERED_ARM]:
            self.filterArmWidget.show()
            if self.main.selectedTool.filterArm is not None:
                self.filterArmImage.setPixmap(
                    self.main.materialLib.lib[self.main.selectedTool.filterArm]['image'].scaled(40, 40))
            self.filterArmL.setText(self.main.selectedTool.filterArm)
            self.selFilterArmB.clicked.connect(lambda: self.main.filterSelectFrame.openMenuAndUpdateInfo(ARM))
            self.selFilterArmB.setStyleCode('White-Square')
            self.selFilterArmB.setEnabled(True)

        # Teleporter DisplayInfo
        if self.main.selectedTool.type in [TELEPORTER_INPUT, TELEPORTER_OUTPUT]:
            self.teleportWidget.show()
            if self.main.selectedTool.teleporterActivated:
                self.TPStatus.setText('Status: Activated')
                self.TPStatus.setStyleCode('Green-Round')
            else:
                self.TPStatus.setText('Status: Deactivated')
                self.TPStatus.setStyleCode('Red-Round')
            self.IDNumL.setText(str(self.main.selectedTool.teleporterID))

    def clearInventory(self):
        self.main.selectedTool.clearInventory()
        self.refreshInventory()

    def refreshInventory(self):
        # Clear Inventory Listing First
        for i in range(0, len(self.inventoryImgL)):
            self.inventoryImgL[i].setPixmap(self.blankImg)
            self.inventoryQtyL[i].setText('-')
            self.inventoryNameL[i].setText('')

        # Fill Values Based on Inventory
        for i, (key, value) in enumerate(self.main.selectedTool.contains.items()):
            self.inventoryImgL[i].setPixmap(self.main.materialLib.lib[key]['image'].scaled(16, 16))
            self.inventoryQtyL[i].setText(str(value))
            self.inventoryNameL[i].setText(key)

    def setStarterQuantity(self, quantity):
        self.main.selectedTool.starterQuantity = quantity

        # Enable Button Based On Research Status
        if self.main.starterMaxSpawnQuantity >= 1:
            self.main.toolPropertiesFrame.changeQty1B.setEnabled(True)
            self.main.toolPropertiesFrame.changeQty1B.setStyleCode('White-Square')
        else:
            self.main.toolPropertiesFrame.changeQty1B.setEnabled(False)
            self.main.toolPropertiesFrame.changeQty1B.setStyleCode('Gray-Square')
        if self.main.starterMaxSpawnQuantity >= 2:
            self.main.toolPropertiesFrame.changeQty2B.setEnabled(True)
            self.main.toolPropertiesFrame.changeQty2B.setStyleCode('White-Square')
        else:
            self.main.toolPropertiesFrame.changeQty2B.setEnabled(False)
            self.main.toolPropertiesFrame.changeQty2B.setStyleCode('Gray-Square')
        if self.main.starterMaxSpawnQuantity >= 3:
            self.main.toolPropertiesFrame.changeQty3B.setEnabled(True)
            self.main.toolPropertiesFrame.changeQty3B.setStyleCode('White-Square')
        else:
            self.main.toolPropertiesFrame.changeQty3B.setEnabled(False)
            self.main.toolPropertiesFrame.changeQty3B.setStyleCode('Gray-Square')

        # Visually Mark Selected Option
        if quantity == 1:
            self.main.toolPropertiesFrame.changeQty1B.setStyleCode('Blue-Square')
        elif quantity == 2:
            self.main.toolPropertiesFrame.changeQty2B.setStyleCode('Blue-Square')
        elif quantity == 3:
            self.main.toolPropertiesFrame.changeQty3B.setStyleCode('Blue-Square')

    def setSplitSetting(self, direction, amount):
        if self.main.selectedTool.splitSetting[direction] + amount >= 1:  # Prevent setting from going below 1
            self.main.selectedTool.splitSetting[direction] += amount
            if self.main.selectedTool.type in [SPLITTER_3WAY, SPLITTER_LEFT, SPLITTER_TEE]:
                self.leftL.setText('%s' % self.main.selectedTool.splitSetting[0])
            if self.main.selectedTool.type in [SPLITTER_3WAY, SPLITTER_LEFT, SPLITTER_RIGHT]:
                self.straightL.setText('%s' % self.main.selectedTool.splitSetting[1])
            if self.main.selectedTool.type in [SPLITTER_3WAY, SPLITTER_RIGHT, SPLITTER_TEE]:
                self.rightL.setText('%s' % self.main.selectedTool.splitSetting[2])
        else:
            self.main.updateMessage('Setting must be greater than zero')

    def setTeleporterID(self, adjustment):
        if self.main.selectedTool.teleporterID is None:
            self.main.selectedTool.teleporterID = 1
        elif self.main.selectedTool.teleporterID + adjustment >= 1:
            self.main.selectedTool.teleporterID += adjustment
        else:
            self.main.updateMessage('Setting must be greater than zero')

        self.main.activateValidTeleporters()

        self.openMenuAndUpdateInfo()
        self.main.raiseFrame(self)


# noinspection PyArgumentList
class blueprintSelectMenu(scrollingBaseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(blueprintSelectMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.titleL.setText('Select Blueprint')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setContentsMargins(100, 20, 100, 20)

        # Generate Blueprints List
        self.wids = {}
        self.cellFrame = {}
        for i, material in enumerate(self.main.materialLib.lib):
            self.wids[material] = {}
            self.wids[material]['base'] = {}
            self.wids[material]['base']['img'] = QLabelImgA(
                '', self.main.materialLib.lib[material]['image'].scaled(32, 32), 'White-None')
            self.wids[material]['base']['label'] = QPushButtonA(material, 'White-Square', 200)

            self.cellFrame[material] = QtWidgets.QFrame()
            self.cellFrame[material].setStyleSheet('background-color: white;\
                                                    border-radius: 6;')
            cellVBox = QtWidgets.QHBoxLayout(self.cellFrame[material])
            cellVBox.addWidget(self.wids[material]['base']['img'])
            cellVBox.addWidget(self.wids[material]['base']['label'])

            self.grid.addWidget(self.cellFrame[material])

        self.contents.setLayout(self.grid)

    def openMenuAndUpdateInfo(self):
        self.main.openMenu(self)

        for i, material in enumerate(self.main.materialLib.lib):
            if self.main.materialLib.lib[material]['class'] \
                    == self.main.machineLib.lib[self.main.selectedTool.type]['blueprintType'] \
                    and material in self.main.unlockedBlueprints:
                self.wids[material]['base']['label'].show()
                self.wids[material]['base']['img'].show()
                self.cellFrame[material].show()
                self.wids[material]['base']['label'].clicked.connect(
                    lambda state, material=material: self.setSelectedBlueprint(material))
            else:
                self.wids[material]['base']['label'].hide()
                self.wids[material]['base']['img'].hide()
                self.cellFrame[material].hide()

            if material == self.main.selectedTool.selectedBlueprint:
                self.wids[material]['base']['label'].setStyleCode('Blue-Square')
            else:
                self.wids[material]['base']['label'].setStyleCode('White-Square')

    def setSelectedBlueprint(self, material):
        self.main.selectedTool.setSelectedBlueprint(material)
        self.main.closeMode()


# noinspection PyArgumentList
class filterSelectMenu(scrollingBaseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(filterSelectMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.titleL.setText('Select Filter')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setContentsMargins(100, 20, 100, 20)

        # Generate Blueprints List
        self.wids = {}
        self.cellFrame = {}
        for i, material in enumerate(self.main.materialLib.lib):
            self.wids[material] = {}
            self.wids[material]['base'] = {}
            self.wids[material]['base']['label'] = QPushButtonA(material, 'White-Square', 200)
            self.wids[material]['base']['img'] = QLabelImgA(
                '', self.main.materialLib.lib[material]['image'].scaled(40, 40), 'White-None')

            self.cellFrame[material] = QtWidgets.QFrame()
            self.cellFrame[material].setStyleSheet('background-color: white; border-radius: 6;')
            cellVBox = QtWidgets.QHBoxLayout()
            cellVBox.addWidget(self.wids[material]['base']['img'])
            cellVBox.addWidget(self.wids[material]['base']['label'])
            self.cellFrame[material].setLayout(cellVBox)
            self.grid.addWidget(self.cellFrame[material])

        self.contents.setLayout(self.grid)

    def openMenuAndUpdateInfo(self, side):
        self.main.openMenu(self)

        for i, material in enumerate(self.main.materialLib.lib):
            self.wids[material]['base']['label'].clicked.connect(
                lambda state, material=material, side=side: self.setFilter(material, side))
            self.wids[material]['base']['label'].setStyleCode('White-Square')
            if side == LEFT and material == self.main.selectedTool.filterLeft:
                self.wids[material]['base']['label'].setStyleCode('Blue-Square')
            if side == RIGHT and material == self.main.selectedTool.filterRight:
                self.wids[material]['base']['label'].setStyleCode('Blue-Square')
            if side == ARM and material == self.main.selectedTool.filterArm:
                self.wids[material]['base']['label'].setStyleCode('Blue-Square')

    def setFilter(self, material, side):
        self.main.closeMode()
        if side == LEFT:
            self.main.selectedTool.filterLeft = material
        elif side == RIGHT:
            self.main.selectedTool.filterRight = material
        elif side == ARM:
            self.main.selectedTool.filterArm = material


# noinspection PyArgumentList,PyArgumentList
class buildMenu(baseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(buildMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMaximumHeight(600)
        self.titleL.setText('Build')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(6)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(3, 1)
        self.grid.setColumnStretch(6, 1)
        self.grid.setColumnStretch(9, 1)
        self.grid.setColumnStretch(12, 1)

        self.setMinimumWidth(1400)

        self.wids = {}
        for i, machine in enumerate(self.main.machineLib.lib):
            self.itemFrame = QtWidgets.QFrame()
            self.itemFrame.setStyleSheet('QFrame{background-color: gray; border: 1px solid black}')
            self.itemGrid = QtWidgets.QGridLayout()
            self.wids[machine] = {}
            self.wids[machine]['img'] = QLabelImgA('', self.main.machineLib.lib[machine]['imageComposite'],
                                                   'White-Square')
            self.wids[machine]['label'] = QPushButtonA(
                '%s - $%s' % (machine, self.main.shortNum(self.main.machineLib.lib[machine]['buildCost'])),
                'White-Round', 230)
            self.wids[machine]['label'].setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.wids[machine]['label'].clicked.connect(lambda state, machine=machine: self.main.buildMode(machine))
            self.itemGrid.addWidget(self.wids[machine]['img'], 0, 0)
            self.itemGrid.addWidget(self.wids[machine]['label'], 0, 1)

            # Create Locked Machines Widgets
            self.wids[machine]['lockImg'] = QLabelImgA('', self.main.imageLib.lib['Key Lock']['image'], 'White-Square')
            self.wids[machine]['lockLabel'] = QPushButtonA(
                'Unlock\n%s - $%s' % (machine, self.main.shortNum(self.main.machineLib.lib[machine]['unlock'])),
                'Blue-Round', 230)
            self.wids[machine]['lockLabel'].setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                          QtWidgets.QSizePolicy.Expanding)
            self.wids[machine]['lockLabel'].clicked.connect(
                lambda state, machine=machine: self.main.unlockMachine(machine))
            self.itemGrid.addWidget(self.wids[machine]['lockImg'], 0, 0)
            self.itemGrid.addWidget(self.wids[machine]['lockLabel'], 0, 1)

            self.itemFrame.setLayout(self.itemGrid)
            self.grid.addWidget(self.itemFrame, (i * 2) % 10, i // 5 * 3 + 1)

        self.contents.setLayout(self.grid)

        self.reset()

    def reset(self):
        for i, machine in enumerate(self.main.machineLib.lib):
            if machine in self.main.unlockedMachines:
                self.wids[machine]['lockImg'].lower()
                self.wids[machine]['lockLabel'].lower()
            else:
                self.wids[machine]['lockImg'].raise_()
                self.wids[machine]['lockLabel'].raise_()


# noinspection PyArgumentList
class blueprintsMenu(scrollingBaseMenuFrame):
    # Setup:
    # contents [grid]
    #    itemframe [itemGrid]
    #        cellFrame [cellGrid]
    def __init__(self, parent=None, main=None):
        super(blueprintsMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMinimumWidth(1000)
        self.titleL.setText('Blueprints')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(2)
        self.grid.setContentsMargins(2, 2, 2, 2)

        # Generate Blueprints List
        self.wids = {}
        for i, material in enumerate(self.main.materialLib.lib):
            if self.main.materialLib.lib[material]['class'] == 'Tier2':  # Exclude Basic & Tier 1 materials
                self.itemFrame = QtWidgets.QFrame()
                self.itemFrame.setContentsMargins(10, 2, 10, 2)

                self.itemGrid = QtWidgets.QGridLayout()
                self.itemGrid.setContentsMargins(10, 2, 10, 2)
                self.itemGrid.setAlignment(QtCore.Qt.AlignLeft)

                self.wids[material] = {}
                self.wids[material]['base'] = {}
                self.wids[material]['base']['label'] = QLabelA('%s' % material, 'Blue-None', None, 11)
                self.wids[material]['base']['img'] = QLabelImgA(
                    '', self.main.materialLib.lib[material]['image'].scaled(32, 32), 'Blue-None')
                self.wids[material]['base']['price'] = QLabelA(
                    '$%s' % self.main.shortNum(self.main.materialLib.lib[material]['value']), 'Blue-None', None, 11)

                cellFrame = QtWidgets.QFrame()
                cellFrame.setStyleSheet('background-color: steelblue;\
                                         border: 1px solid black;\
                                         border-radius: 4')
                cellFrame.setFixedSize(180, 100)
                cellGrid = QtWidgets.QGridLayout()
                cellGrid.setContentsMargins(2, 0, 2, 2)
                cellGrid.addWidget(self.wids[material]['base']['label'], 0, 0, 1, 2)
                cellGrid.addWidget(self.wids[material]['base']['img'], 1, 1, 1, 1)
                cellGrid.addWidget(self.wids[material]['base']['price'], 1, 0, 1, 1)
                cellFrame.setLayout(cellGrid)

                cellFrame.setContentsMargins(10, 2, 10, 10)

                self.itemGrid.addWidget(cellFrame, 1, 1, 1, 1, QtCore.Qt.AlignCenter)
                self.itemGrid.setColumnMinimumWidth(1, 200)  # Only changes left frame column width
                self.itemGrid.setRowMinimumHeight(1, 120)

                # Add Lock Widgets Over Components
                self.wids[material]['base']['lock'] = QPushButtonA(
                    'Unlock Blueprint\n$%s' % self.main.shortNum(self.main.materialLib.lib[material]['unlock']),
                    'MediumGray-Round')
                self.wids[material]['base']['lock'].setFixedSize(550, 100)
                self.itemGrid.addWidget(self.wids[material]['base']['lock'], 1, 2, 1, 3, QtCore.Qt.AlignCenter)
                self.wids[material]['base']['lock'].clicked.connect(
                    lambda state, material=material: self.main.unlockBlueprint(material))

                # Create cover to place in front of lock button when item is unlocked
                self.wids[material]['base']['cover'] = QLabelA('', 'LightGray-Round')
                self.itemGrid.addWidget(self.wids[material]['base']['cover'], 1, 1, 1, 4)

                # Add components for each item
                for j, component in enumerate(self.main.materialLib.lib[material]['components']):
                    self.wids[material][j] = {}
                    self.wids[material][j]['label'] = QLabelA('%s' % component, 'White-None', None, 11)
                    self.wids[material][j]['img'] = QLabelImgA(
                        '', self.main.materialLib.lib[component]['image'].scaled(24, 24), 'White-None')
                    self.wids[material][j]['qty'] = QLabelA(
                        '%s' % self.main.materialLib.lib[material]['components'][component], 'White-None')

                    self.wids[material][j]['qty'].setMargin(10)  # Margin around the qty label

                    cellFrame = QtWidgets.QFrame()
                    cellFrame.setStyleSheet('background-color: white;\
                                             border: 1px solid black;\
                                             border-radius: 6')
                    cellFrame.setFixedSize(180, 100)

                    cellGrid = QtWidgets.QGridLayout(cellFrame)
                    cellGrid.setContentsMargins(10, 2, 10, 10)
                    cellGrid.addWidget(self.wids[material][j]['label'], 0, 0, 1, 2)
                    cellGrid.addWidget(self.wids[material][j]['img'], 1, 1, 1, 1, QtCore.Qt.AlignLeft)
                    cellGrid.addWidget(self.wids[material][j]['qty'], 1, 0, 1, 1, QtCore.Qt.AlignRight)

                    cellFrame.setContentsMargins(0, 0, 0, 0)

                    self.itemGrid.addWidget(cellFrame, 1, j + 2, 1, 1, QtCore.Qt.AlignCenter)

                # self.itemFrame.setMinimumWidth(1000)
                self.itemFrame.setLayout(self.itemGrid)
                self.grid.addWidget(self.itemFrame, i, 1)

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(5, 1)

        self.contents.setLayout(self.grid)

        self.reset()

    def reset(self):
        # Mark Locked Widgets Only
        for i, material in enumerate(self.main.materialLib.lib):
            if self.main.materialLib.lib[material]['class'] == 'Tier2':  # Exclude Basic and Tier1 from listing
                if material in self.main.unlockedBlueprints:
                    self.wids[material]['base']['cover'].lower()
                    self.wids[material]['base']['lock'].lower()
                else:
                    self.wids[material]['base']['cover'].lower()
                    self.wids[material]['base']['lock'].raise_()


# noinspection PyArgumentList,PyArgumentList,PyArgumentList
class researchMenu(scrollingBaseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(researchMenu, self).__init__(parent, main)

        self.setMinimumWidth(1000)

        # Set Menu Parameters
        self.titleL.setText('Research')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(40, 40, 40, 40)

        # List of research options with information
        self.wids = {}
        for i, option in enumerate(self.main.researchLib.lib):
            self.wids[option] = {}
            self.wids[option]['desc'] = QLabelA(
                '%s' % str(self.main.researchLib.lib[option]['description']), 'White-None', 400)
            self.wids[option]['desc'].setWordWrap(True)
            self.wids[option]['lock'] = QPushButtonA(
                'Unlock for $%s' %
                self.main.shortNum(self.main.researchLib.lib[option]['cost']), 'MediumGray-Round', 200)
            self.wids[option]['lock'].clicked.connect(lambda state, option=option: self.main.unlockResearch(option))

            cellFrame = QtWidgets.QFrame()
            cellFrame.setStyleSheet('QFrame{background-color: white;\
                                     border: 1px solid black;\
                                     border-radius: 4}')
            cellGrid = QtWidgets.QGridLayout()
            cellGrid.setSpacing(6)
            cellGrid.addWidget(self.wids[option]['desc'], 0, 0, 1, 1, QtCore.Qt.AlignCenter)
            cellGrid.addWidget(self.wids[option]['lock'], 2, 0, 1, 1, QtCore.Qt.AlignCenter)
            cellFrame.setLayout(cellGrid)

            self.grid.setRowMinimumHeight(i * 2, 120)
            self.grid.addWidget(cellFrame, i // 2, i % 2 + 1)

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(3, 1)

        self.contents.setLayout(self.grid)

        self.reset()

    def reset(self):
        for i, option in enumerate(self.main.researchLib.lib):
            if option in self.main.unlockedResearch:
                self.wids[option]['lock'].setText('Unlocked')
                self.wids[option]['lock'].setDisabled(1)
                self.wids[option]['lock'].setStyleCode('Green-Round')
            else:
                self.wids[option]['lock'].setText(
                    'Unlock for $%s' % self.main.shortNum(self.main.researchLib.lib[option]['cost']))
                self.wids[option]['lock'].setDisabled(0)
                self.wids[option]['lock'].setStyleCode('MediumGray-Round')


# noinspection PyArgumentList,PyArgumentList,PyArgumentList,PyArgumentList,PyUnresolvedReferences
class assyLineMenu(baseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(assyLineMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMaximumHeight(600)
        self.titleL.setText('Assembly Lines')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(20, 20, 20, 20)

        self.line2BLocked = QPushButtonA('Unlock Assembly Line 2 - $10M', 'MediumGray-Round', 300)
        self.line2BLocked.clicked.connect(lambda state: self.main.buyAssyLine('Line2', 10000000))
        self.grid.addWidget(self.line2BLocked, 0, 0)

        self.line3BLocked = QPushButtonA('Unlock Assembly Line 3 - $500M', 'MediumGray-Round', 300)
        self.line3BLocked.clicked.connect(lambda state: self.main.buyAssyLine('Line3', 500000000))
        self.grid.addWidget(self.line3BLocked, 1, 0)

        self.contents.setLayout(self.grid)

        self.reset()

    def reset(self):
        if 'Line2' in self.main.unlockedAssyLines:
            self.line2BLocked.setText('Assembly Line 2 - Unlocked')
            self.line2BLocked.setDisabled(True)
            self.line2BLocked.setStyleCode('Green-Round')
        else:
            self.line2BLocked.setText('Unlock Assembly Line 2 - $5M')
            self.line2BLocked.setDisabled(False)
            self.line2BLocked.setStyleCode('MediumGray-Round')

        if 'Line3' in self.main.unlockedAssyLines:
            self.line3BLocked.setText('Assembly Line 2 - Unlocked')
            self.line3BLocked.setDisabled(True)
            self.line3BLocked.setStyleCode('Green-Round')
        elif 'Line2' not in self.main.unlockedAssyLines:
            self.line3BLocked.setText('Assembly Line 3 - Not Available')
            self.line3BLocked.setDisabled(True)
            self.line3BLocked.setStyleCode('MediumGray-Round')
        else:
            self.line3BLocked.setText('Unlock Assembly Line 3 - $500M')
            self.line3BLocked.setDisabled(False)
            self.line3BLocked.setStyleCode('MediumGray-Round')


# noinspection PyArgumentList
class helpMenu(scrollingBaseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(helpMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMinimumWidth(1000)
        self.titleL.setText('Help')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(40, 40, 40, 40)

        # List of help list items
        self.wids = {}
        for i, machine in enumerate(self.main.machineLib.lib):
            self.wids[machine] = {}
            self.wids[machine]['name'] = QLabelA(machine, 'White-None', None, 14)
            self.wids[machine]['image'] = QLabelImgA(
                '', self.main.machineLib.lib[machine]['imageComposite'], 'White-None')
            self.wids[machine]['prop1'] = QLabelA(
                'Build Cost: $%s' % self.main.shortNum(self.main.machineLib.lib[machine]['buildCost']), 'White-None')
            self.wids[machine]['prop2'] = QLabelA(
                'Electricity Cost: $%s' % self.main.shortNum(self.main.machineLib.lib[machine]['opCost']),
                'White-None')
            self.wids[machine]['desc'] = QLabelA(
                'Description: %s' % self.main.machineLib.lib[machine]['description'], 'White-None')

            self.wids[machine]['desc'].setWordWrap(True)

            cellFrame = QtWidgets.QFrame()
            cellFrame.setStyleSheet('background-color: white;\
                                     border: 1px solid black;\
                                     border-radius: 6;')
            cellGrid = QtWidgets.QGridLayout()
            cellGrid.setSpacing(10)
            cellGrid.addWidget(self.wids[machine]['name'], 0, 1, 1, 3)
            cellGrid.addWidget(self.wids[machine]['image'], 1, 1, 3, 1)
            cellGrid.addWidget(self.wids[machine]['prop1'], 2, 2, 1, 1)
            cellGrid.addWidget(self.wids[machine]['prop2'], 2, 3, 1, 1)
            cellGrid.addWidget(self.wids[machine]['desc'], 3, 2, 1, 2)

            cellGrid.setColumnMinimumWidth(1, 100)
            cellGrid.setColumnMinimumWidth(2, 200)
            cellGrid.setColumnMinimumWidth(3, 200)
            cellGrid.setColumnStretch(0, 1)
            cellGrid.setColumnStretch(4, 1)

            cellFrame.setLayout(cellGrid)

            self.grid.addWidget(cellFrame, i * 2, 1)

            self.grid.setRowMinimumHeight(i * 2, 80)
            self.grid.setRowMinimumHeight(i * 2 + 1, 6)

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(5, 1)

        self.contents.setLayout(self.grid)


# noinspection PyArgumentList
class incomeAnalysisMenu(baseMenuFrame):
    # noinspection PyDictCreation
    def __init__(self, parent=None, main=None):
        super(incomeAnalysisMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMaximumHeight(600)
        self.titleL.setText('Income\n(%s Second Intervals)' % INCOME_ANALYSIS_FREQ)

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.grid.setContentsMargins(50, 50, 50, 50)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(5, 1)

        self.wids = {}
        self.wids['MRHeader_Type'] = QLabelA('Resource', 'White-Square-Table-Title', 300)
        self.wids['MRHeader_Count'] = QLabelA('Count', 'White-Square-Table-Title', 150)
        self.wids['MRHeader_Profit'] = QLabelA('Profit', 'White-Square-Table-Title', 150)
        self.wids['MRHeader_PPS'] = QLabelA('Profit/s', 'White-Square-Table-Title', 150)
        self.grid.addWidget(self.wids['MRHeader_Type'], 0, 1)
        self.grid.addWidget(self.wids['MRHeader_Count'], 0, 2)
        self.grid.addWidget(self.wids['MRHeader_Profit'], 0, 3)
        self.grid.addWidget(self.wids['MRHeader_PPS'], 0, 4)

        for i in range(0, 9):
            self.wids[i] = {}
            self.wids[i]['Type'] = QLabelA('', 'White-Square-Table')
            self.wids[i]['Count'] = QLabelA('', 'White-Square-Table')
            self.wids[i]['Profit'] = QLabelA('', 'White-Square-Table')
            self.wids[i]['PPS'] = QLabelA('', 'White-Square-Table')

            self.grid.addWidget(self.wids[i]['Type'], i + 1, 1)
            self.grid.addWidget(self.wids[i]['Count'], i + 1, 2)
            self.grid.addWidget(self.wids[i]['Profit'], i + 1, 3)
            self.grid.addWidget(self.wids[i]['PPS'], i + 1, 4)

        self.contents.setLayout(self.grid)

        self.reset()

    def reset(self):
        for i in range(0, 9):
            self.wids[i]['Type'].setText('')
            self.wids[i]['Count'].setText('')
            self.wids[i]['Profit'].setText('')
            self.wids[i]['PPS'].setText('')


# noinspection PyArgumentList
class frameRateMenu(baseMenuFrame):
    # noinspection PyDictCreation
    def __init__(self, parent=None, main=None):
        super(frameRateMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMaximumHeight(660)
        self.setMinimumHeight(660)
        self.titleL.setText('Frame Rate Analysis\n(Last %s Frames ~ %i Seconds )'
                            % (FRAME_RATE_ANALYSIS_LOG_SIZE, int(CYCLE_INTERVAL * FRAME_RATE_ANALYSIS_LOG_SIZE / 1000)))

        # Set Grid Contents
        layout = QtWidgets.QVBoxLayout()

        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.grid.setAlignment(QtCore.Qt.AlignCenter)

        self.wids = {}
        self.wids['MRHeader_Frames'] = QLabelA('Frames', 'White-Square-Table-Title', 150)
        self.wids['MRHeader_Setpoint'] = QLabelA('Setpoint (ms)', 'White-Square-Table-Title', 150)
        self.wids['MRHeader_Target'] = QLabelA('High Limit', 'White-Square-Table-Title', 150)
        self.wids['MRHeader_High'] = QLabelA('High Frames', 'White-Square-Table-Title', 150)
        self.wids['MRHeader_Highest'] = QLabelA('Highest', 'White-Square-Table-Title', 150)
        self.wids['MRHeader_FPS'] = QLabelA('Average FPS', 'White-Square-Table-Title', 150)
        self.grid.addWidget(self.wids['MRHeader_Frames'], 0, 0)
        self.grid.addWidget(self.wids['MRHeader_Setpoint'], 0, 1)
        self.grid.addWidget(self.wids['MRHeader_Target'], 0, 2)
        self.grid.addWidget(self.wids['MRHeader_High'], 0, 3)
        self.grid.addWidget(self.wids['MRHeader_Highest'], 0, 4)
        self.grid.addWidget(self.wids['MRHeader_FPS'], 0, 5)

        self.wids['Frames'] = QLabelA('-', 'White-Square-Table')
        self.wids['Setpoint'] = QLabelA('-', 'White-Square-Table')
        self.wids['High Limit'] = QLabelA('-', 'White-Square-Table')
        self.wids['High'] = QLabelA('-', 'White-Square-Table')
        self.wids['Highest'] = QLabelA('-', 'White-Square-Table')
        self.wids['AverageFPS'] = QLabelA('-', 'White-Square-Table')

        self.grid.addWidget(self.wids['Frames'], 1, 0)
        self.grid.addWidget(self.wids['Setpoint'], 1, 1)
        self.grid.addWidget(self.wids['High Limit'], 1, 2)
        self.grid.addWidget(self.wids['High'], 1, 3)
        self.grid.addWidget(self.wids['Highest'], 1, 4)
        self.grid.addWidget(self.wids['AverageFPS'], 1, 5)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setContentsMargins(40, 40, 40, 40)
        layout.addWidget(self.canvas)
        layout.addLayout(self.grid)
        self.contents.setLayout(layout)

        self.reset()

    def openMenuAndUpdateInfo(self):
        self.main.openMenu(self)
        self.main.frameRateAnalyze()

    def plot(self):
        yAxisData = self.main.frameRateResultSet  # Latest data point at end of list
        xAxisDataBase = [i for i in range(-600, 0, 1)]  # [-600, -599... -1]
        xAxisData = xAxisDataBase[-len(yAxisData):]  # Slice end portion to match length of yAxisData

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(xAxisData, yAxisData, 'o', markersize=3)  # Data points
        numFrames = FRAME_RATE_ANALYSIS_LOG_SIZE
        ax.plot([-numFrames, 0], [int(CYCLE_INTERVAL * 0.9), int(CYCLE_INTERVAL * 0.9)],
                color='r', linestyle='-', linewidth=1)  # Lower limit line
        ax.plot([-numFrames, 0], [int(CYCLE_INTERVAL * 1.5), int(CYCLE_INTERVAL * 1.5)],
                color='r', linestyle='-', linewidth=1)  # Upper limit line
        ax.set_xlabel('Frame Number')
        ax.set_ylabel('Time (ms)')
        ax.set_ylim([0, 140])
        self.canvas.draw()

    def reset(self):
        for i in range(0, 9):
            self.wids['Frames'].setText('-')
            self.wids['High Limit'].setText('-')
            self.wids['High'].setText('-')
            self.wids['Highest'].setText('-')


# noinspection PyArgumentList,PyArgumentList,PyArgumentList
class achievementsMenu(scrollingBaseMenuFrame):
    def __init__(self, parent=None, main=None):
        super(achievementsMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMinimumWidth(1000)
        self.titleL.setText('Achievements Unlocked')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(6)
        self.grid.setContentsMargins(40, 40, 40, 40)

        # Populate list of achievements
        self.wids = {}
        for i, item in enumerate(list(self.main.achievementLib.lib) + list(self.main.materialLib.lib)):
            self.wids[item] = {}
            self.wids[item]['name'] = QLabelA(item, 'White-None', None, 14)

            if item in self.main.materialLib.lib:
                self.wids[item]['desc'] = QLabelA('Sell one %s' % item, 'White-None')
            else:
                self.wids[item]['desc'] = QLabelA(self.main.achievementLib.lib[item]['description'], 'White-None')

            self.wids[item]['cellFrame'] = QtWidgets.QFrame()
            self.wids[item]['cellFrame'].setFixedWidth(280)
            self.wids[item]['cellFrame'].setStyleSheet('background-color: white;\
                                                       border: 1px solid black;\
                                                       border-radius: 6;')
            cellVBox = QtWidgets.QVBoxLayout(self.wids[item]['cellFrame'])
            cellVBox.addWidget(self.wids[item]['name'])
            cellVBox.addWidget(self.wids[item]['desc'])

            self.grid.addWidget(self.wids[item]['cellFrame'], i // 3, i % 3 + 1)

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(5, 1)

        self.contents.setLayout(self.grid)

        self.reset()

    def reset(self):
        for item in self.main.achievementLib.lib:
            if item in self.main.unlockedAchievements:
                self.wids[item]['cellFrame'].setStyleSheet('background-color: green;\
                                                            border: 1px solid black;\
                                                            border-radius: 6;')
                self.wids[item]['name'].setStyleCode('Green-None')
                self.wids[item]['desc'].setStyleCode('Green-None')
            else:
                self.wids[item]['cellFrame'].setStyleSheet('background-color: white;\
                                                            border: 1px solid black;\
                                                            border-radius: 6;')
                self.wids[item]['name'].setStyleCode('White-None')
                self.wids[item]['desc'].setStyleCode('White-None')

        for item in self.main.materialLib.lib:
            if item in self.main.unlockedAchievements:
                self.wids[item]['cellFrame'].setStyleSheet('background-color: green;\
                                                            border: 1px solid black;\
                                                            border-radius: 6;')
                self.wids[item]['name'].setStyleCode('Green-None')
                self.wids[item]['desc'].setStyleCode('Green-None')
            else:
                self.wids[item]['cellFrame'].setStyleSheet('background-color: white;\
                                                            border: 1px solid black;\
                                                            border-radius: 6;')
                self.wids[item]['name'].setStyleCode('White-None')
                self.wids[item]['desc'].setStyleCode('White-None')


# noinspection PyArgumentList,PyArgumentList
class floorPlanMenu(baseMenuFrame):
    # noinspection PyDictCreation
    def __init__(self, parent=None, main=None):
        super(floorPlanMenu, self).__init__(parent, main)

        # Set Menu Parameters
        self.setMaximumHeight(600)
        self.titleL.setText('Floor Plans')

        # Set Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.grid.setContentsMargins(50, 50, 50, 50)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(7, 1)

        self.wids = {}
        self.wids['headerName'] = QLabelA('Number', 'White-Square-Table-Title', 100)
        self.wids['headerDesc'] = QLabelA('Description', 'White-Square-Table-Title', 300)
        self.wids['headerSize'] = QLabelA('Size', 'White-Square-Table-Title', 100)
        self.wids['name'] = QLabelA('Name', 'White-Square-Table-Title', 80)
        self.wids['buy'] = QLabelA('Buy', 'White-Square-Table-Title', 80)
        self.wids['create'] = QLabelA('Create', 'White-Square-Table-Title', 80)

        self.grid.addWidget(self.wids['headerName'], 0, 1)
        self.grid.addWidget(self.wids['headerDesc'], 0, 2)
        self.grid.addWidget(self.wids['headerSize'], 0, 3)
        self.grid.addWidget(self.wids['name'], 0, 4)
        self.grid.addWidget(self.wids['buy'], 0, 5)
        self.grid.addWidget(self.wids['create'], 0, 6)

        # Add Lock Widget Over Plans
        self.floorPlanFeatureLock = QLabelA('Research Floor Plans to Unlock', 'Gray-Square')
        self.grid.addWidget(self.floorPlanFeatureLock, 0, 0, 11, 8)
        self.floorPlanFeatureLock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        for i in range(0, 10):  # 10 plans, 0 thru 9
            self.wids[i] = {}
            self.wids[i]['num'] = QLabelA('-', 'White-Square-Table')
            self.wids[i]['name'] = QLabelA('-', 'White-Square-Table')
            self.wids[i]['entry'] = QtWidgets.QLineEdit(self.main.floorPlans[i]['description'])
            self.wids[i]['size'] = QLabelA('-', 'White-Square-Table')
            self.wids[i]['save'] = QPushButtonA('Save', 'Blue-Square', 80)
            self.wids[i]['edit'] = QPushButtonA('Edit', 'White-Square-Table', 80)
            self.wids[i]['place'] = QPushButtonA('Place', 'White-Square-Table', 80)
            self.wids[i]['new'] = QPushButtonA('New', 'White-Square-Table', 80)

            self.wids[i]['entry'].setMinimumHeight(24)
            self.wids[i]['edit'].setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.wids[i]['place'].setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.wids[i]['new'].setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

            # self.wids[i]['name'].setAlignment(QtCore.Qt.AlignLeft)
            self.wids[i]['entry'].setStyleSheet('QLineEdit{background-color: steelblue;\
                                                border: 1px solid black;\
                                                color: white;}')

            self.wids[i]['edit'].clicked.connect(lambda state, i=i: self.editFloorPlanName(i))
            self.wids[i]['new'].clicked.connect(lambda state, i=i: self.main.newFloorPlanSelTopLeftMode(i))
            self.wids[i]['place'].clicked.connect(lambda state, i=i: self.main.placeFloorPlanSelTopLeftMode(i))
            self.wids[i]['save'].clicked.connect(lambda state, i=i: self.saveFloorPlanName(i))

            self.grid.addWidget(self.wids[i]['num'], i + 1, 1)
            self.grid.addWidget(self.wids[i]['entry'], i + 1, 2)
            self.grid.addWidget(self.wids[i]['name'], i + 1, 2)
            self.grid.addWidget(self.wids[i]['size'], i + 1, 3)
            self.grid.addWidget(self.wids[i]['save'], i + 1, 4)
            self.grid.addWidget(self.wids[i]['edit'], i + 1, 4)
            self.grid.addWidget(self.wids[i]['place'], i + 1, 5)
            self.grid.addWidget(self.wids[i]['new'], i + 1, 6)

        self.contents.setLayout(self.grid)

        self.reset()

    def reset(self):
        for i in range(0, 10):
            self.wids[i]['num'].setText(str(i + 1))
            self.wids[i]['name'].setText('-')
            self.wids[i]['size'].setText('-')

        for i, (plan, value) in enumerate(self.main.floorPlans.items()):
            self.wids[i]['name'].setText('%s' % self.main.floorPlans[plan]['description'])
            # noinspection PyStringFormat
            self.wids[i]['size'].setText('%i x %i' % self.main.floorPlans[i]['size'])

        if 'floorPlansFeatureUnlock' in self.main.unlockedResearch:
            self.floorPlanFeatureLock.hide()
        else:
            self.floorPlanFeatureLock.show()
            self.floorPlanFeatureLock.raise_()

    def editFloorPlanName(self, i):
        self.wids[i]['save'].raise_()
        self.wids[i]['entry'].raise_()
        self.wids[i]['entry'].setFocus()

    def saveFloorPlanName(self, i):
        self.wids[i]['save'].lower()
        self.wids[i]['entry'].lower()
        self.main.floorPlans[i]['description'] = self.wids[i]['entry'].text()
        self.wids[i]['name'].setText(self.main.floorPlans[i]['description'])


# noinspection PyArgumentList
class achievementPopUpMenu(QtWidgets.QFrame):
    def __init__(self, parent=None, main=None):
        super(achievementPopUpMenu, self).__init__(parent)
        self.parent = parent
        self.main = main

        # Frame Setup
        self.setMaximumHeight(140)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setStyleSheet('QFrame{background-color: green;\
                           border: 1px solid black;\
                           border-radius: 6;}')
        self.setMinimumWidth(400)
        self.wids = {}

        # Grid Contents
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(20, 20, 20, 20)

        self.achievementName = QLabelA('Achievement Name', 'Green-None', 300)
        self.grid.addWidget(self.achievementName, 0, 0)

        # Frame's Layout
        self.setLayout(self.grid)

        self.reset()

    def reset(self):
        self.achievementName.setText('None')


# -------- MainApp Class -------- #

# noinspection PyArgumentList,PyUnresolvedReferences,PyUnresolvedReferences
class clsMainApp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(clsMainApp, self).__init__(parent)
        print('\nRunning...')

        self.Tiles = []  # List of all Tiles
        self.Machines = []  # List of all Machines
        self.oMachines = []  # List of all Machines frozen at start of each iteration
        self.Materials = []  # List of all Materials
        self.oMaterials = []  # List of all Materials frozen at start of each iteration
        self.iteration = 0  # Initialize iteration
        self.iterationStartTime = datetime.datetime.now()
        self.messageTimer = 0
        self.eventTimer = 0
        self.achievementTimer = 0
        self.achievementPop = None
        self.queueReset = False  # Initialize queue reset flag
        self.balance = None  # Initialize balance
        self.tilePrice = 1000  # Initialize price per tile
        self.teleporterInputIDs = {}  # ID, [Objects with that ID]
        self.teleporterOutputIDs = {}  # ID, [Objects with that ID]
        self.machineLib = machineLib()
        self.materialLib = materialLib()
        self.researchLib = researchLib()
        self.achievementLib = achievementLib()
        self.imageLib = imageLib()
        self.xClick = None
        self.yClick = None
        self.xClickTileCenter = None
        self.yClickTileCenter = None
        self.xCursorTileCenter = None
        self.yCursorTileCenter = None
        self.selFloorPlan = None
        self.floorPlanTopLeft = None
        self.floorPlanBottomRight = None
        self.thetaAB = None
        self.thetaBC = None
        self.xRelB = None
        self.yRelB = None
        self.xRelC = None
        self.yRelC = None
        self.xRelLinkCenterAB = None
        self.yRelLinkCenterAB = None
        self.xRelLinkCenterBC = None
        self.yRelLinkCenterBC = None
        self.angledPixmapLink1 = None
        self.angledPixmapLink2 = None
        self.timer = None
        self.timeLogEnabled = False
        self.timeLog = []  # List of timestamps and information for time profiling
        self.updateNewFloorPlanVisualsFlag = False
        self.updatePlaceFloorPlanVisualsFlag = False
        self.floorPlans = {}
        for i in range(0, 10):  # Plans # 0 to 9
            self.floorPlans[i] = {}
            self.floorPlans[i]['size'] = (0, 0)
            self.floorPlans[i]['description'] = ''
            self.floorPlans[i]['machines'] = {}
        self.unlockedMachines = []
        self.unlockedBlueprints = []
        self.unlockedTiles = []
        self.unlockedAssyLines = []
        self.unlockedAchievements = []
        self.unlockedResearch = []
        self.opCostModifier = None  # Research modifier variables
        self.maxStarters = None
        self.maxTeleporters = None
        self.opTimeModifierStarterCrafter = None
        self.opTimeModifierTier2Machines = None
        self.starterMaxSpawnQuantity = None
        self.machineToBeMoved = None
        self.moneyRate = 0  # Money analysis variables
        self.itemRate = 0
        self.lastMRAnalysisTime = datetime.datetime.now()
        self.salesCollector = {}
        self.salesAnalysis = {}
        self.clickedTool = None
        self.clickedTile = None
        self.selectedTool = None
        self.selectedMenu = None
        self.frameRateResultSet = []  # Frame rate analysis variables
        self.lastFrameRateAnalysisTime = datetime.datetime.now()

        self.machineBlueprintList = {}  # Pre-computed dictionary of considered blueprints for each machine type
        for machineType in [DRAWER, CUTTER, FURNACE, PRESS]:
            self.machineBlueprintList[machineType] = []
            for material in self.materialLib.lib:
                if self.materialLib.lib[material]['class'] == self.machineLib.lib[machineType]['blueprintType']:
                    self.machineBlueprintList[machineType].append(material)

        # Menu Geometry Setup
        self.sceneWidth = 1250  # Scene Width
        self.sceneHeight = 400  # Scene Height
        self.appWidth = 1400  # Overall window width
        self.appHeight = 600  # Overall window height

        # App Icon
        self.setWindowIcon(QtGui.QIcon('images/icon.png'))

        # Menu Bar
        mainMenu = self.menuBar()

        saveAction = QtWidgets.QAction("&Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip('Save Game - Ctrl+S')
        saveAction.triggered.connect(self.saveConfig)

        zoomInAction = QtWidgets.QAction("Zoom In", self)
        zoomInAction.setShortcut("Ctrl++")
        zoomInAction.setStatusTip('Zoom In - Ctrl+I')
        zoomInAction.triggered.connect(lambda: self.viewFrameZoom(IN))

        zoomOutAction = QtWidgets.QAction("Zoom Out", self)
        zoomOutAction.setShortcut("Ctrl+-")
        zoomOutAction.setStatusTip('Load Game - Ctrl+O')
        zoomOutAction.triggered.connect(lambda: self.viewFrameZoom(OUT))

        zoomResetAction = QtWidgets.QAction("Zoom Reset", self)
        zoomResetAction.setShortcut("Ctrl+Z")
        zoomResetAction.setStatusTip('Reset Zoom - Ctrl+Z')
        zoomResetAction.triggered.connect(lambda: self.viewFrameZoom(RESET))

        loadAction = QtWidgets.QAction("&Load", self)
        loadAction.setShortcut("Ctrl+L")
        loadAction.setStatusTip('Load Game - Ctrl+L')
        loadAction.triggered.connect(self.loadConfig)

        resetAction = QtWidgets.QAction("&Reset", self)
        resetAction.setShortcut("Ctrl+R")
        resetAction.setStatusTip('Reset Game - Ctrl+R')
        resetAction.triggered.connect(self.reset)

        cancelAction = QtWidgets.QAction("Cancel", self)
        cancelAction.setShortcut("ESCAPE")
        cancelAction.setStatusTip('Cancel - Escape')
        cancelAction.triggered.connect(self.closeMode)

        startTimeLogAction = QtWidgets.QAction("Start Time Log", self)
        startTimeLogAction.setShortcut("")
        startTimeLogAction.setStatusTip('Start Time Log')
        startTimeLogAction.triggered.connect(self.startTimeLog)

        stopTimeLogAction = QtWidgets.QAction("Stop Time Log", self)
        stopTimeLogAction.setShortcut("")
        stopTimeLogAction.setStatusTip('Stop Time Log')
        stopTimeLogAction.triggered.connect(self.stopTimeLog)

        exitAction = QtWidgets.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+W')
        exitAction.setStatusTip('Exit - Ctrl+W')
        exitAction.triggered.connect(sys.exit)

        mainMenu.addAction(saveAction)
        mainMenu.addAction(zoomInAction)
        mainMenu.addAction(zoomOutAction)
        mainMenu.addAction(zoomResetAction)
        mainMenu.addAction(loadAction)
        mainMenu.addAction(resetAction)
        mainMenu.addAction(cancelAction)
        mainMenu.addAction(startTimeLogAction)
        mainMenu.addAction(stopTimeLogAction)
        mainMenu.addAction(exitAction)

        # Main Window Setup
        self.setStyleSheet('QMainWindow{background-color: white}')
        self.setWindowTitle('Factory')
        self.scene = QtWidgets.QGraphicsScene(self)

        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setMinimumHeight(30)
        self.statusBar.setStyleSheet('background-color: white; border-top: 1px solid black')
        font = QtGui.QFont()
        font.setPointSize(10)
        self.statusBar.setFont(font)
        self.statusBar.showMessage('None')

        self.resize(self.appWidth, self.appHeight)

        self.singleSW, self.singleSH, self.combinedSW, self.combinedSH = self.getSystemInfo()
        if self.combinedSW < 2600:  # Single screen detected
            self.move(int((self.singleSW - self.appWidth) / 2), int((self.singleSH - self.appHeight) / 2 - 300))
        else:  # Dual screen detected
            self.move(int((self.singleSW - self.appWidth) / 2 + 1900), int((self.singleSH - self.appHeight) / 2 - 240))

        # Widget Setup
        self.wids = {}
        self.db = {}
        self.dbfile = None

        self.coreLoop = clsCoreLoop(self)  # Instantiate the coreLoop

        # Draw Grid Lines
        for i in range(0, 400 + 1, 25):  # Create horizontal grid lines
            self.scene.addItem(QtWidgets.QGraphicsLineItem(0, i, 1250, i))
        for i in range(0, 1250 + 1, 25):  # Create vertical grid lines
            self.scene.addItem(QtWidgets.QGraphicsLineItem(i, 0, i, 400))

        # Header Dock Widget
        self.headerDockWidget = QtWidgets.QFrame()
        self.headerDockWidget.setMinimumHeight(70)
        self.headerDockWidget.setMinimumHeight(70)
        self.headerDockWidget.setStyleSheet('QFrame{background: steelblue}')
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(2)
        self.grid.setColumnMinimumWidth(1, 5)

        self.appTitle = QLabelA('Factory', 'Blue-None-White-Large', 400)

        self.grid.setColumnStretch(7, 1)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vboxsub1 = QtWidgets.QVBoxLayout()
        self.vboxsub2 = QtWidgets.QVBoxLayout()

        self.vboxsub1.addWidget(self.appTitle)
        self.vboxsub1.setAlignment(QtCore.Qt.AlignCenter)

        self.vboxsub2.addLayout(self.grid)

        self.vbox.addLayout(self.vboxsub1)
        self.vbox.addLayout(self.vboxsub2)

        self.vbox.setAlignment(QtCore.Qt.AlignCenter)

        self.headerDockWidget.setLayout(self.vbox)

        # Upper Dock Widget
        self.upperDockWidget = QtWidgets.QFrame()
        self.upperDockWidget.setMinimumHeight(90)
        self.upperDockWidget.setStyleSheet('QFrame{background: rgb(220,220,220); border-top: 1px solid black}}')
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(6)
        self.grid.setColumnMinimumWidth(1, 5)

        self.balance_label = QLabelA('Balance:', 'White-Round', 400)
        self.metric_label = QLabelA('0 / %i Achievements Unlocked' % self.getAmountOfAchievements(), 'White-Round', 400)
        self.moneyRate_label = QLabelA('-', 'White-Round', 400)
        self.itemRate_label = QLabelA('-:', 'White-Round', 400)
        self.message_label = QLabelA('-', 'White-Round', 800)
        self.event_label = QLabelA('-', 'White-Round', 800)

        self.balance_label.setFixedHeight(32)
        self.metric_label.setFixedHeight(32)
        self.moneyRate_label.setFixedHeight(32)
        self.itemRate_label.setFixedHeight(32)
        self.message_label.setFixedHeight(32)
        self.event_label.setFixedHeight(32)

        self.grid.setColumnStretch(0, 1)
        self.grid.addWidget(self.balance_label, 1, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.metric_label, 1, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.moneyRate_label, 1, 3, 1, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.itemRate_label, 1, 4, 1, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.message_label, 2, 1, 1, 2, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.event_label, 2, 3, 1, 2, QtCore.Qt.AlignCenter)
        self.grid.setColumnStretch(5, 1)

        self.upperDockWidget.setLayout(self.grid)

        # Lower Dock Widget
        self.lowerDockWidget = QtWidgets.QFrame()
        self.lowerDockWidget.setStyleSheet('QFrame{background: rgb(220,220,220)}')
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(0)

        self.move_button = QPushButtonA('Move', 'White-Square-Menu-Left-Side', 150)
        self.rotate_button = QPushButtonA('Rotate', 'White-Square-Menu-Left-Side', 150)
        self.sell_button = QPushButtonA('Sell', 'White-Square-Menu-Left-Side', 150)
        self.tiles_button = QPushButtonA('Purchase Tiles', 'White-Square-Menu-Left-Side', 150)
        self.cancel_button = QPushButtonA('Cancel', 'White-Square-Menu-Right-Side', 150)

        self.build_button = QPushButtonA('Build', 'White-Square-Menu-Left-Side', 150)
        self.blueprints_button = QPushButtonA('Blueprints', 'White-Square-Menu-Left-Side', 150)
        self.research_button = QPushButtonA('Research', 'White-Square-Menu-Left-Side', 150)
        self.buyLine_button = QPushButtonA('Buy Assy Lines', 'White-Square-Menu-Left-Side', 150)
        self.analysis_button = QPushButtonA('Income', 'White-Square-Menu-Right-Side', 150)

        self.achievements_button = QPushButtonA('Achievements', 'White-Square-Menu-Bottom-Side', 150)
        self.help_button = QPushButtonA('Help', 'White-Square-Menu-Bottom-Side', 150)
        self.floorPlan_button = QPushButtonA('Floor Plans', 'White-Square-Menu-Bottom-Side', 150)
        self.frameRate_button = QPushButtonA('FPS', 'White-Square-Menu-Bottom-Side', 150)
        self.debug_button = QPushButtonA('Debug', 'White-Square', 150)

        self.grid.setColumnStretch(0, 1)

        self.grid.addWidget(self.move_button, 1, 1)
        self.grid.addWidget(self.rotate_button, 1, 2)
        self.grid.addWidget(self.sell_button, 1, 3)
        self.grid.addWidget(self.tiles_button, 1, 4)
        self.grid.addWidget(self.cancel_button, 1, 5)

        self.grid.addWidget(self.build_button, 2, 1)
        self.grid.addWidget(self.blueprints_button, 2, 2)
        self.grid.addWidget(self.research_button, 2, 3)
        self.grid.addWidget(self.buyLine_button, 2, 4)
        self.grid.addWidget(self.analysis_button, 2, 5)

        self.grid.addWidget(self.achievements_button, 3, 1)
        self.grid.addWidget(self.help_button, 3, 2)
        self.grid.addWidget(self.floorPlan_button, 3, 3)
        self.grid.addWidget(self.frameRate_button, 3, 4)
        self.grid.addWidget(self.debug_button, 3, 5)

        self.grid.setColumnStretch(9, 1)

        self.lowerDockWidget.setLayout(self.grid)

        # Create Central Container Widget
        self.container = QtWidgets.QWidget()
        self.container.setContentsMargins(10, 10, 10, 10)
        self.container.setObjectName('container')  # Name stylesheet to prevent inherited style
        self.container.setStyleSheet('#container{background-color: rgb(240,240,240);\
                                      border: 1px solid black}')
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.containerGrid = QtWidgets.QGridLayout()
        self.containerGrid.setColumnStretch(0, 1)
        self.containerGrid.setRowStretch(0, 1)

        # Initiate View Menu Frames
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setFixedSize(1300, 440)
        self.viewFrame = QtWidgets.QFrame()
        self.viewFrame.setContentsMargins(10, 10, 10, 10)
        self.viewFrame.setStyleSheet('background-color: white;\
                                      border: 1px solid black}')
        self.viewFrameVBox = QtWidgets.QVBoxLayout()
        self.viewFrameVBox.setAlignment(QtCore.Qt.AlignCenter)
        self.viewFrameVBox.addStretch(1)
        self.viewFrameVBox.addWidget(self.view)
        self.viewFrameVBox.addStretch(1)
        self.viewFrame.setLayout(self.viewFrameVBox)

        # Zoom Settings
        self.scaleFactor = 1
        self.view.scale(self.scaleFactor, self.scaleFactor)

        # For mousing position tracking for highlight tile visuals
        self.scene.installEventFilter(self)

        # Instantiate Menu Frames
        self.buildMenuFrame = buildMenu(main=self)
        self.blueprintsMenuFrame = blueprintsMenu(main=self)
        self.researchMenuFrame = researchMenu(main=self)
        self.assyLineMenuFrame = assyLineMenu(main=self)
        self.incomeAnalysisMenuFrame = incomeAnalysisMenu(main=self)
        self.frameRateMenuFrame = frameRateMenu(main=self)
        self.achievementsMenuFrame = achievementsMenu(main=self)
        self.helpMenuFrame = helpMenu(main=self)
        self.floorPlanMenuFrame = floorPlanMenu(main=self)
        self.toolPropertiesFrame = toolPropertiesMenu(main=self)  # One window for many tools
        self.blueprintSelectFrame = blueprintSelectMenu(main=self)  # One window for many tools
        self.filterSelectFrame = filterSelectMenu(main=self)  # One window for many tools
        self.achievementPopUpMenuFrame = achievementPopUpMenu(main=self)  # Only achievement pop-up frame

        self.containerGrid.addWidget(self.viewFrame, 0, 0)  # Don't align center if want to fill space
        self.containerGrid.addWidget(self.buildMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.blueprintsMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.researchMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.assyLineMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.achievementsMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.incomeAnalysisMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.frameRateMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.helpMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.floorPlanMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.toolPropertiesFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.blueprintSelectFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.filterSelectFrame, 0, 0, QtCore.Qt.AlignHCenter)
        self.containerGrid.addWidget(self.achievementPopUpMenuFrame, 0, 0, QtCore.Qt.AlignHCenter)

        # Connect Button Signals
        self.move_button.clicked.connect(self.moveMode)
        self.rotate_button.clicked.connect(self.rotateMode)
        self.sell_button.clicked.connect(self.sellMode)
        self.tiles_button.clicked.connect(self.buyTilesMode)
        self.cancel_button.clicked.connect(self.closeMode)
        self.build_button.clicked.connect(lambda: self.openMenu(self.buildMenuFrame))
        self.blueprints_button.clicked.connect(lambda: self.openMenu(self.blueprintsMenuFrame))
        self.research_button.clicked.connect(lambda: self.openMenu(self.researchMenuFrame))
        self.buyLine_button.clicked.connect(lambda: self.openMenu(self.assyLineMenuFrame))
        self.analysis_button.clicked.connect(lambda: self.openMenu(self.incomeAnalysisMenuFrame))
        self.achievements_button.clicked.connect(lambda: self.openMenu(self.achievementsMenuFrame))
        self.help_button.clicked.connect(lambda: self.openMenu(self.helpMenuFrame))
        self.floorPlan_button.clicked.connect(lambda: self.openMenu(self.floorPlanMenuFrame))
        self.frameRate_button.clicked.connect(self.frameRateMenuFrame.openMenuAndUpdateInfo)
        self.debug_button.clicked.connect(self.debugMode)

        # Set Main Layout
        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainVLayout.setSpacing(0)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)
        self.mainVLayout.addWidget(self.headerDockWidget)
        self.mainVLayout.addWidget(self.upperDockWidget)
        self.mainVLayout.addWidget(self.container)
        self.mainVLayout.addWidget(self.lowerDockWidget)

        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setLayout(self.mainVLayout)

        self.container.setLayout(self.containerGrid)
        self.raiseFrame(self.viewFrame)
        self.setCentralWidget(self.mainWidget)
        self.show()
        self.closeMode()

    def raiseFrame(self, frame):
        self.viewFrame.raise_()
        frame.raise_()

    @staticmethod
    def lowerFrame(frame):
        frame.lower()

    def openMenu(self, frame):
        self.closeMode()  # Don't clear selected tool when opening menu
        self.raiseFrame(frame)
        self.selectedMenu = frame
        self.move_button.setEnabled(False)
        self.rotate_button.setEnabled(False)
        self.sell_button.setEnabled(False)
        self.tiles_button.setEnabled(False)

    def closeMode(self):
        self.deselectAllButtons()
        self.viewFrame.raise_()
        self.selectedMenu = None
        self.delAllHighlights()
        self.delAllArrows()
        self.scene.mouseReleaseEvent = lambda event: self.showToolProperties(event)
        self.view.setMouseTracking(False)  # Unbind mouse tracking
        self.updateNewFloorPlanVisualsFlag = False  # Stop displaying visuals
        self.updatePlaceFloorPlanVisualsFlag = False  # Stop displaying visuals
        self.statusBar.showMessage('None')
        self.move_button.setEnabled(True)
        self.rotate_button.setEnabled(True)
        self.sell_button.setEnabled(True)
        self.tiles_button.setEnabled(True)

    def debugMode(self):
        pass
        # self.updateBalance(999999999)

    def clicked(self, event):
        point = event.buttonDownScenePos(QtCore.Qt.LeftButton)
        self.xClick = point.x()
        self.yClick = self.sceneHeight - point.y()  # Scene and grid coordinates systems differ
        self.xClickTileCenter, self.yClickTileCenter = self.getTileCenter(self.xClick, self.yClick)
        self.clickedTile = self.getTile(self.xClickTileCenter, self.yClickTileCenter)
        self.clickedTool = self.getMachine(self.xClickTileCenter, self.yClickTileCenter)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.GraphicsSceneMouseMove:  # Not all events are mousemove with pos()
            if self.updateNewFloorPlanVisualsFlag is True:
                self.updateNewFloorPlanVisuals(event)  # Highlights selected tiles
            if self.updatePlaceFloorPlanVisualsFlag is True:
                self.updatePlaceFloorPlanVisuals(event)  # Highlights selected tiles
        return super(clsMainApp, self).eventFilter(source, event)

    def showToolProperties(self, event):
        self.clicked(event)
        if self.clickedTool:
            self.selectedTool = self.clickedTool
            self.toolPropertiesFrame.openMenuAndUpdateInfo()

    def viewFrameZoom(self, direction):
        if direction == IN:
            self.view.setTransform(QtGui.QTransform())  # Reset
            self.view.scale(2, 2)  # 2.0x
        if direction == OUT:
            self.view.setTransform(QtGui.QTransform())  # Reset
            self.view.scale(0.5, 0.5)  # 0.5x
        if direction == RESET:
            self.view.setTransform(QtGui.QTransform())  # Reset

    def buildMachineAttempt(self, event, machine):
        self.clicked(event)
        if not self.clickedTool:
            if self.clickedTile is not None \
                    and not self.clickedTile.locked \
                    and not self.clickedTile.walled \
                    and self.clickedTool is None:
                self.buildMachineIfAbleToBuildAny(
                    machine, self.clickedTile.x, self.clickedTile.y, 'D', None, 1, None, None, 1)
            else:
                self.updateMessage('Invalid Location')

    def buildMachineIfAbleToBuildAny(self, machine, x, y, orientation, selectedBlueprint, starterQuantity, filterLeft,
                                     filterRight, teleportID):
        # Checks balance & max machine limits
        if machine == STARTER and self.maxStarters is not None \
                and self.getNumberMachinesInClickedAssyLine(STARTER) >= self.maxStarters:
            # noinspection PyStringFormat
            self.updateMessage('Maximum amount of Starters (%i) already placed in this line' % self.maxStarters)
        elif machine == TELEPORTER_INPUT and self.maxStarters is not None \
                and self.getNumberMachinesInClickedAssyLine(TELEPORTER_INPUT) >= self.maxTeleporters:
            # noinspection PyStringFormat
            self.updateMessage('Maximum amount of Teleporters (%i) already placed in this line' % self.maxTeleporters)
        else:
            self.Machines.append(clsMachine(self, machine, x, y, orientation,
                                            selectedBlueprint, starterQuantity, filterLeft, filterRight, teleportID))
            self.updateBalance(self.balance - self.machineLib.lib[machine]['buildCost'])
            self.updateMessage(
                'Purchased %s for $%s' % (machine, self.shortNum(self.machineLib.lib[machine]['buildCost'])))

    def buildMode(self, machine):
        self.closeMode()
        self.build_button.setStyleCode('Blue-Square-Menu-Left-Side')
        self.scene.mouseReleaseEvent = lambda event, machine=machine: self.buildMachineAttempt(event, machine)
        self.statusBar.showMessage('Select location to build %s' % machine)

    def moveMode(self):
        self.closeMode()
        self.move_button.setStyleCode('Blue-Square-Menu-Left-Side')
        self.scene.mouseReleaseEvent = lambda event: self.moveMachineFrom(event)
        self.statusBar.showMessage('Select machine to move')
        self.updateMessage('Select Machine To Move')

    def moveMachineFrom(self, event):
        self.clicked(event)
        self.statusBar.showMessage('Select new machine location')
        if self.clickedTool:
            self.machineToBeMoved = self.clickedTool
            self.clickedTile.drawShape(HIGHLIGHT)
            self.updateMessage('Select Destination')
            self.scene.mouseReleaseEvent = lambda event: self.moveMachineTo(event)
        else:
            self.statusBar.showMessage('Invalid Selection, Select Machine To Move')

    def moveMachineTo(self, event):
        self.clicked(event)
        if not self.clickedTile.locked and not self.clickedTile.walled and self.clickedTool is None:
            self.machineToBeMoved.moveMachine(self.xClickTileCenter, self.yClickTileCenter)
            self.machineToBeMoved = None
            self.delAllHighlights()
            self.moveMode()
        else:
            self.statusBar.showMessage('Invalid location, select new location')

    def rotateMode(self):
        self.deselectAllButtons()
        self.rotate_button.setStyleCode('Blue-Square-Menu-Left-Side')
        self.drawAllArrows()
        self.scene.mouseReleaseEvent = lambda event: self.rotateMachineAttempt(event)
        self.statusBar.showMessage('Select machine to rotate')

    def rotateMachineAttempt(self, event):
        self.clicked(event)
        if self.clickedTool:
            self.clickedTool.rotateMachine()

    def sellMode(self):
        self.deselectAllButtons()
        self.sell_button.setStyleCode('Blue-Square-Menu-Left-Side')
        self.statusBar.showMessage('Select machine to sell')
        self.scene.mouseReleaseEvent = lambda event: self.sellMachineAttempt(event)

    def sellMachineAttempt(self, event):
        self.clicked(event)
        if self.clickedTool:
            self.clickedTool.sellMachine()

    def buyTilesMode(self):
        self.deselectAllButtons()
        self.tiles_button.setStyleCode('Blue-Square-Menu-Left-Side')
        self.scene.mouseReleaseEvent = lambda event: self.buyTileAttempt(event)
        self.statusBar.showMessage('Purchase a Tile for $%s' % self.shortNum(self.getTilePrice()))

    def buyTileAttempt(self, event):
        self.clicked(event)
        if self.clickedTile.locked is True and self.clickedTile.walled is False:
            if self.balance >= self.getTilePrice():
                self.clickedTile.buyTile()
            else:
                self.updateMessage('Not enough money')
        else:
            self.updateMessage('Tile not available for purchase')

    def getTilePrice(self):
        # Tiles	    1	        80	        160         320             480
        # Price	    15,000      103,000     725,200     35,968,200      1,784,039,000
        # From Exponential curve fit of targets, minus free tiles
        price = 14620 * math.exp(0.0244 * (len(self.unlockedTiles) - 288))
        return int(round(price, -2))  # Ranges from ~$15k to ~$1.5B, rounded to 100

    def newFloorPlanSelTopLeftMode(self, planNum):
        self.closeMode()
        self.floorPlan_button.setStyleCode('Blue-Square-Menu-Bottom-Side')
        self.selFloorPlan = planNum
        self.floorPlan_button.setStyleCode('Blue-White-Square-Menu-Bottom-Side')
        self.statusBar.showMessage('Select top left corner to start creating floor plan')
        for tile in self.Tiles:  # Pre-draw tile highlights & setVisibility
            tile.drawShape(HIGHLIGHT)
            tile.shape_highlight.setZValue(Z_HIGHLIGHT)
            tile.shape_highlight.setVisible(False)
        self.scene.mouseReleaseEvent = lambda event: self.newFloorPlanSelBotRightMode(event)

    def newFloorPlanSelBotRightMode(self, event):
        self.clicked(event)
        self.floorPlanTopLeft = self.clickedTile
        self.floorPlanTopLeft.drawShape(HIGHLIGHT)
        self.view.setMouseTracking(True)  # Start mouse tracking
        self.updateNewFloorPlanVisualsFlag = True  # Start displaying visuals
        self.statusBar.showMessage('Select bottom right corner to create floor plan')
        self.scene.mouseReleaseEvent = lambda event: self.newFloorPlanSaveMode(event)

    def newFloorPlanSaveMode(self, event):
        self.clicked(event)
        self.floorPlanBottomRight = self.clickedTile
        self.updateNewFloorPlanVisualsFlag = False  # Stop displaying visuals
        self.view.setMouseTracking(False)  # Stop mouse tracking

        selectedTools = []
        selectedTools.clear()
        for tool in self.Machines:
            if self.floorPlanTopLeft.x <= tool.x <= self.floorPlanBottomRight.x \
                    and self.floorPlanBottomRight.y <= tool.y <= self.floorPlanTopLeft.y:
                selectedTools.append(tool)

        self.floorPlans[self.selFloorPlan]['description'] = 'Saved Floor Plan %i' % (self.selFloorPlan + 1)

        self.floorPlans[self.selFloorPlan]['size'] = (
            int((self.floorPlanBottomRight.x - self.floorPlanTopLeft.x) / 25) + 1,
            int((self.floorPlanTopLeft.y - self.floorPlanBottomRight.y) / 25) + 1)

        # Loop thru machines in selected area to store location and properties
        xBottomLeftCorner = self.floorPlanTopLeft.x
        yBottomLeftCorner = self.floorPlanBottomRight.y
        self.floorPlans[self.selFloorPlan]['machines'].clear()
        for i, tool in enumerate(selectedTools):
            xRelative = tool.x - xBottomLeftCorner
            yRelative = tool.y - yBottomLeftCorner
            self.floorPlans[self.selFloorPlan]['machines'][i] = [tool.type, xRelative, yRelative, tool.orientation,
                                                                 tool.selectedBlueprint, tool.starterQuantity,
                                                                 tool.filterLeft, tool.filterRight, tool.teleporterID]
        self.floorPlanMenuFrame.reset()
        self.updateMessage('Floor Plan Saved!')
        self.closeMode()
        self.openMenu(self.floorPlanMenuFrame)

    def updateNewFloorPlanVisuals(self, event):
        point = event.scenePos()
        xCursor = point.x()
        yCursor = self.sceneHeight - point.y()

        x, y = self.getTileCenter(xCursor, yCursor)  # Check if cursor changed tiles or don't waste time updating
        if (x, y) != (self.xCursorTileCenter, self.yCursorTileCenter):
            self.xCursorTileCenter, self.yCursorTileCenter = x, y

            for tile in self.Tiles:
                if self.floorPlanTopLeft.x <= tile.x <= self.xCursorTileCenter \
                        and self.yCursorTileCenter <= tile.y <= self.floorPlanTopLeft.y:
                    tile.shape_highlight.setVisible(True)
                else:
                    tile.shape_highlight.setVisible(False)

    def placeFloorPlanSelTopLeftMode(self, planNum):
        self.closeMode()
        self.floorPlan_button.setStyleCode('Blue-Square-Menu-Bottom-Side')
        self.selFloorPlan = planNum
        for tile in self.Tiles:  # Pre-draw tile highlights & setVisibility
            tile.drawShape(HIGHLIGHT)
            tile.shape_highlight.setZValue(Z_HIGHLIGHT)
            tile.shape_highlight.setVisible(False)
        self.view.setMouseTracking(True)  # Start mouse tracking
        self.updatePlaceFloorPlanVisualsFlag = True  # Flag starts visuals
        self.statusBar.showMessage('Mode: Select valid location to place floor plan')
        self.scene.mouseReleaseEvent = lambda event: self.placeSelectedFloorPlan(event)

    def placeSelectedFloorPlan(self, event):
        self.clicked(event)
        self.floorPlanBottomRight = self.clickedTile
        if self.checkValidFloorPlanSpacing(self.clickedTile) is True:
            for key, value in self.floorPlans[self.selFloorPlan]['machines'].items():
                self.buildMachineIfAbleToBuildAny(value[0],
                                                  value[1] + self.clickedTile.x,  # Conv self.floorPlan rel x, y to abs
                                                  value[2] + self.clickedTile.y,
                                                  *value[3:])
            self.updateMessage('Floor Plan Placed!')
        else:
            self.updateMessage('Invalid Area Selected')

    def checkValidFloorPlanSpacing(self, spot):
        i, j = self.floorPlans[self.selFloorPlan]['size']  # i, j = number of tiles in self.floorPlan

        # Check if floor plan will fit within scene area
        if spot.x + i * 25 > 1250 and spot.y + j * 25 > 400:
            return False

        for tile in self.Tiles:
            if spot.x <= tile.x <= (spot.x + (i - 1) * 25) and spot.y <= tile.y <= (spot.y + (j - 1) * 25):

                # Check if tile is locked or walled
                if tile.walled is True or tile.locked is True:
                    return False  # Tile is locked or walled

                # Check if tile contains a machine
                for tool in self.Machines:
                    if (tool.x, tool.y) == (tile.x, tile.y):
                        return False  # Tile is occupied
        return True

    def updatePlaceFloorPlanVisuals(self, event):
        point = event.scenePos()
        xCursor = point.x()
        yCursor = self.sceneHeight - point.y()

        i, j = self.floorPlans[self.selFloorPlan]['size']

        x, y = self.getTileCenter(xCursor, yCursor)  # Check if cursor changed tiles or don't re-update
        if (x, y) != (self.xCursorTileCenter, self.yCursorTileCenter):
            self.xCursorTileCenter, self.yCursorTileCenter = x, y

            for tile in self.Tiles:
                if self.xCursorTileCenter <= tile.x <= (self.xCursorTileCenter + (i - 1) * 25) \
                        and self.yCursorTileCenter <= tile.y <= (self.yCursorTileCenter + (j - 1) * 25):
                    tile.shape_highlight.setVisible(True)
                else:
                    tile.shape_highlight.setVisible(False)

    def deselectAllButtons(self):
        self.build_button.setStyleCode('White-Square-Menu-Left-Side')
        self.move_button.setStyleCode('White-Square-Menu-Left-Side')
        self.rotate_button.setStyleCode('White-Square-Menu-Left-Side')
        self.tiles_button.setStyleCode('White-Square-Menu-Left-Side')
        self.sell_button.setStyleCode('White-Square-Menu-Left-Side')
        self.floorPlan_button.setStyleCode('White-Square-Menu-Bottom-Side')
        self.cancel_button.setStyleCode('White-Square-Menu-Right-Side')
        self.delAllArrows()

    def finishSetup(self):
        self.initializeValues()
        self.generateTileList()
        self.resetUnlockedParameterLists()
        self.markTilesLockedOrUnlocked()
        self.markAllTilesWalledOrNot()
        self.resetAllMenus()
        self.precomputeRoboticArmKinematics()
        self.startCoreLoopTimer()

    def startCoreLoopTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.coreLoop.run)
        self.timer.start(CYCLE_INTERVAL)

    def saveConfig(self):
        self.db.clear()
        self.db['machines'] = {}
        for i, tool in enumerate(self.Machines):
            self.db['machines'][i] = [tool.type, tool.x, tool.y, tool.orientation,
                                      tool.selectedBlueprint, tool.starterQuantity,
                                      tool.filterLeft, tool.filterRight, tool.teleporterID, tool.filterArm]
        self.db['balance'] = self.balance
        self.db['unlockedMachines'] = self.unlockedMachines
        self.db['unlockedBlueprints'] = self.unlockedBlueprints
        self.db['unlockedResearch'] = self.unlockedResearch
        self.db['unlockedAssyLines'] = self.unlockedAssyLines
        self.db['unlockedAchievements'] = self.unlockedAchievements
        self.db['unlockedTiles'] = self.unlockedTiles
        self.db['starterMaxSpawnQuantity'] = self.starterMaxSpawnQuantity
        self.db['maxStarters'] = self.maxStarters
        self.db['maxTeleporters'] = self.maxTeleporters
        self.db['opCostModifier'] = self.opCostModifier
        self.db['opTimeModifierStarterCrafter'] = self.opTimeModifierStarterCrafter
        self.db['opTimeModifierTier2Machines'] = self.opTimeModifierTier2Machines
        self.db['floorPlans'] = self.floorPlans

        self.dbfile = open('saveFile', 'wb')  # w = overwrite, a = append
        pickle.dump(self.db, self.dbfile)
        self.dbfile.close()
        self.updateMessage('Game Saved!')
        self.statusBar.showMessage('Game Saved!')

    def loadConfig(self):
        self.reset()

        self.db.clear()
        self.db['machines'] = {}
        self.dbfile = open('saveFile', 'rb')
        self.db = pickle.load(self.dbfile)
        self.dbfile.close()

        for key, value in self.db['machines'].items():
            self.Machines.append(clsMachine(self, *value))
        self.updateBalance(self.db['balance'])
        self.unlockedMachines = self.db['unlockedMachines']
        self.unlockedBlueprints = self.db['unlockedBlueprints']
        self.unlockedResearch = self.db['unlockedResearch']
        self.unlockedAssyLines = self.db['unlockedAssyLines']
        self.unlockedAchievements = self.db['unlockedAchievements']
        self.unlockedTiles = self.db['unlockedTiles']
        self.starterMaxSpawnQuantity = self.db['starterMaxSpawnQuantity']
        self.maxStarters = self.db['maxStarters']
        self.maxTeleporters = self.db['maxTeleporters']
        self.opCostModifier = self.db['opCostModifier']
        self.opTimeModifierStarterCrafter = self.db['opTimeModifierStarterCrafter']
        self.opTimeModifierTier2Machines = self.db['opTimeModifierTier2Machines']
        self.floorPlans = self.db['floorPlans']

        self.markTilesLockedOrUnlocked()  # Load changes due to self.unlockedTiles
        self.markAllTilesWalledOrNot()  # Load changes due to self.unlockedAssyLines
        self.resetAllMenus()  # Load changes due to changed parameters
        self.metric_label.setText(
            '%i / %i Achievements Unlocked' % (len(self.unlockedAchievements), self.getAmountOfAchievements()))
        self.updateMessage('Game Loaded!')
        self.statusBar.showMessage('Game Loaded!')

        _LOGGER.debug(self.db.keys())
        _LOGGER.debug(self.db)

        # Debugging - Remove all selected & considered blueprints from Starters & Crafters
        # for machine in self.Machines:
        #     if machine.type in [STARTER, CRAFTER]:
        #         machine.consideredBlueprints = []
        #         machine.selectedBlueprint = None

        # Debugging - Unlock blueprint manually
        # self.unlockedBlueprints.append('Speaker')
        # self.maxStarters = 35

    def reset(self):
        self.deleteAllMachinesAndMaterials()
        self.salesCollector.clear()  # Delete everything in achievements sales collector
        self.resetUnlockedParameterLists()
        self.markTilesLockedOrUnlocked()
        self.markAllTilesWalledOrNot()
        self.removeAchievementNotification()  # Remove any open notification
        self.initializeValues()  # Set variables to initial values
        self.resetAllMenus()
        self.closeMode()
        self.queueReset = False
        self.metric_label.setText(
            '%i / %i Achievements Unlocked' % (len(self.unlockedAchievements), self.getAmountOfAchievements()))
        self.updateMessage('Game Reset!')
        self.statusBar.showMessage('Game Reset!')

    def resetUnlockedParameterLists(self):
        self.unlockedMachines = [STARTER, SELLER]
        self.unlockedBlueprints = [
            'Copper', 'Gold', 'Iron', 'Aluminum', 'Crystal',
            'Copper Wire', 'Gold Wire', 'Iron Wire', 'Aluminum Wire', 'Crystal Wire',
            'Copper Gear', 'Gold Gear', 'Iron Gear', 'Aluminum Gear', 'Crystal Gear',
            'Molten Copper', 'Molten Gold', 'Molten Iron', 'Molten Aluminum', 'Molten Crystal',
            'Copper Plate', 'Gold Plate', 'Iron Plate', 'Aluminum Plate', 'Crystal Plate',
            'Circuit'
        ]
        self.unlockedResearch.clear()
        self.unlockedAssyLines.clear()
        self.unlockedAchievements.clear()
        self.unlockedTiles.clear()
        # Index of tiles to mark as always unlocked
        for i in list(range(0, 96)) + list(range(272, 368)) + list(range(544, 640)):
            self.unlockedTiles.append((self.Tiles[i].x, self.Tiles[i].y))

    def resetAllMenus(self):
        self.buildMenuFrame.reset()
        self.blueprintsMenuFrame.reset()
        self.researchMenuFrame.reset()
        self.assyLineMenuFrame.reset()
        self.achievementsMenuFrame.reset()
        self.incomeAnalysisMenuFrame.reset()
        self.floorPlanMenuFrame.reset()

    def deleteAllMachinesAndMaterials(self):
        while len(self.Machines) > 0:  # Deleting items in list modifies index
            self.Machines[0].delMachine()

        while len(self.Materials) > 0:  # Deleting items in list modifies index
            self.Materials[0].delMaterial()

    def initializeValues(self):
        self.balance = 15000  # Proper initial balance for new game is 15,000
        # self.balance = 500000000000  # Balance for debugging

        self.balance_label.setText('Balance: $%s' % '{:,}'.format(self.balance))
        self.moneyRate_label.setText('Profit: $%s / Second' % '{:,}'.format(self.moneyRate))
        self.itemRate_label.setText('Sales: %s Items / Second' % '{:,}'.format(self.itemRate))
        self.statusBar.showMessage('None')
        self.message_label.setText('New Game!')

        self.opCostModifier = 1  # OpCost = 5,3,1 so mod starts 1 and goes down by 0.4 twice
        self.maxStarters = 10  # Max per line
        self.maxTeleporters = 10  # Max per all lines combined
        self.opTimeModifierStarterCrafter = 0  # Is 0 and inc 1 2x, op_time is 3s and dec 1s 2x
        self.opTimeModifierTier2Machines = 0  # Is 0 and inc 1 2x, op_time is 3s and dec 1s 2x
        self.starterMaxSpawnQuantity = 1  # Starts at 1 max and goes up by 1 twice

    def setQueueReset(self):
        self.queueReset = True

    def generateTileList(self):  # Create a list with all tiles objects
        self.Tiles.clear()
        for i in range(13, self.sceneWidth, 25):
            for j in range(13, self.sceneHeight, 25):
                self.Tiles.append(clsTile(self, i, j))

    def markTilesLockedOrUnlocked(self):
        for tile in self.Tiles:
            if (tile.x, tile.y) in self.unlockedTiles:
                tile.markAsUnlocked()
            else:
                tile.markAsLocked()

    def buyAssyLine(self, lineNumber, price):
        if self.balance >= price:
            if lineNumber == 'Line2':
                self.unlockedAssyLines.append(lineNumber)
                self.markAllTilesWalledOrNot()
                self.assyLineMenuFrame.reset()

            elif lineNumber == 'Line3':
                self.unlockedAssyLines.append(lineNumber)
                self.markAllTilesWalledOrNot()
                self.assyLineMenuFrame.reset()

            self.updateBalance(self.balance - price)
            self.updateMessage('Bought new Assy Line line for $%s!' % self.shortNum(price))
        else:
            self.updateMessage('Not enough money')

    def markAllTilesWalledOrNot(self):
        if 'Line2' in self.unlockedAssyLines:
            [self.Tiles[i].markAsUnwalled() for i in range(272, 528)]
        else:
            [self.Tiles[i].markAsWalled() for i in range(272, 528)]
        if 'Line3' in self.unlockedAssyLines:
            [self.Tiles[i].markAsUnwalled() for i in range(544, 800)]
        else:
            [self.Tiles[i].markAsWalled() for i in range(544, 800)]
        [self.Tiles[i].markAsWalled() for i in list(range(256, 272)) + list(range(528, 544))]  # Border walls

    def getNumberMachinesInClickedAssyLine(self, machineType):
        machineCount = 0
        for tool in self.Machines:
            if tool.type == machineType and tool.assyLine == self.clickedTile.assyLine:
                machineCount += 1
        return machineCount

    def updateBalance(self, newBalance):
        self.balance = int(newBalance)
        self.balance_label.setText('Balance: $%s' % '{:,}'.format(self.balance))

    def updateMessage(self, message):
        self.message_label.setText(message)
        self.messageTimer = self.iteration

    def updateEvent(self, event):
        self.event_label.setText(event)
        self.eventTimer = self.iteration

    def checkAchievements(self):
        # Check for material sales achievements
        for key, value in self.salesCollector.items():
            if key not in self.unlockedAchievements:
                self.unlockedAchievements.append(key)
                self.achievementsMenuFrame.reset()
                self.achievementNotification('Sold %s' % key)

        # Check for profit per second achievements
        if 'Profit I' not in self.unlockedAchievements and self.moneyRate >= 1000000:
            self.unlockedAchievements.append('Profit I')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Profit I')
        if 'Profit II' not in self.unlockedAchievements and self.moneyRate >= 10000000:
            self.unlockedAchievements.append('Profit II')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Profit II')
        if 'Profit III' not in self.unlockedAchievements and self.moneyRate >= 100000000:
            self.unlockedAchievements.append('Profit III')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Profit III')

        # Check for sales per second achievements
        if 'Scale I' not in self.unlockedAchievements and self.itemRate >= 1:
            self.unlockedAchievements.append('Scale I')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Scale I')
        if 'Scale II' not in self.unlockedAchievements and self.itemRate >= 5:
            self.unlockedAchievements.append('Scale II')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Scale II')
        if 'Scale III' not in self.unlockedAchievements and self.itemRate >= 10:
            self.unlockedAchievements.append('Scale III')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Scale III')

        # Check for all possible items sold achievement
        if 'Sell Every Items' not in self.unlockedAchievements \
                and all(k in self.unlockedAchievements for k in list(self.materialLib.lib.keys())):
            self.unlockedAchievements.append('Sell Every Items')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Sell Every Items')

        # Check for all possible assembly lines unlocked achievement
        if 'Max Assembly Lines' not in self.unlockedAchievements \
                and all(k in self.unlockedAssyLines for k in ['Line2', 'Line3']):
            self.unlockedAchievements.append('Max Assembly Lines')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Max Assembly Lines')

        # Check for all possible research options unlocked achievement
        if 'Unlock All Research' not in self.unlockedAchievements \
                and all(k in self.unlockedAchievements for k in list(self.researchLib.lib.keys())):
            self.unlockedAchievements.append('Unlock All Research')
            self.achievementsMenuFrame.reset()
            self.achievementNotification('Unlock All Research')

    def achievementNotification(self, title):
        self.achievementTimer = self.iteration
        self.achievementPopUpMenuFrame.achievementName.setText('Achievement Unlocked!\n%s' % title)
        self.metric_label.setText(
            '%i / %i Achievements Unlocked' % (len(self.unlockedAchievements), self.getAmountOfAchievements()))
        self.achievementPopUpMenuFrame.raise_()

    def removeAchievementNotification(self):
        self.lowerFrame(self.achievementPopUpMenuFrame)

    def getAmountOfAchievements(self):
        return len(self.achievementLib.lib) - 1 + len(self.materialLib.lib)  # Sell each item plus others

    def fadeMessage(self):
        if not self.message_label.text().startswith(' '):
            self.updateMessage('  ' + str(self.message_label.text()))

    def fadeEvent(self):
        if not self.event_label.text().startswith(' '):
            self.updateEvent('  ' + str(self.event_label.text()))

    def activateValidTeleporters(self):  # Prevents multiple inputs going to same output
        self.teleporterInputIDs.clear()  # [ID], [Objects with that matching ID]
        self.teleporterOutputIDs.clear()  # [ID], [Objects with that matching ID]

        for tool in self.Machines:
            if tool.type == TELEPORTER_INPUT:
                # Return value for key if exists else return empty list, can't use append because list is destroyed
                self.teleporterInputIDs[tool.teleporterID] = \
                    self.teleporterInputIDs.setdefault(tool.teleporterID, []) + [tool]
            if tool.type == TELEPORTER_OUTPUT:
                # Return value for key if exists else return empty list, can't use append because list is destroyed
                self.teleporterOutputIDs[tool.teleporterID] = \
                    self.teleporterOutputIDs.setdefault(tool.teleporterID, []) + [tool]

        for key, value in self.teleporterInputIDs.items():
            if len(value) > 1:
                for tool in value:
                    tool.teleporterActivated = False
            else:
                for tool in value:
                    tool.teleporterActivated = True

        for key, value in self.teleporterOutputIDs.items():
            if len(value) > 1:
                for tool in value:
                    tool.teleporterActivated = False
            else:
                for tool in value:
                    tool.teleporterActivated = True

    def moneyRateAnalyze(self):
        self.lastMRAnalysisTime = datetime.datetime.now()
        self.salesAnalysis = self.salesCollector.copy()  # Make a copy of salesCollector
        self.salesCollector.clear()

        totalIncome = 0  # Reset totalIncome to 0
        totalSales = 0  # Reset sales to 0
        if self.salesAnalysis:  # Check that dictionary is not empty
            for i, (key, value) in enumerate(self.salesAnalysis.items()):
                if i < 9:
                    self.incomeAnalysisMenuFrame.wids[i]['Type'].setText(key)
                    self.incomeAnalysisMenuFrame.wids[i]['Count'].setText(str(value))
                    self.incomeAnalysisMenuFrame.wids[i]['Profit'].setText(
                        '$' + str(self.shortNum(self.materialLib.lib[key]['value'] * value)))
                    self.incomeAnalysisMenuFrame.wids[i]['PPS'].setText(
                        '$' + str(self.shortNum(self.materialLib.lib[key]['value'] * value / INCOME_ANALYSIS_FREQ)))
                totalIncome += self.materialLib.lib[key]['value'] * value / INCOME_ANALYSIS_FREQ
                totalSales += value / INCOME_ANALYSIS_FREQ
        self.moneyRate_label.setText('Profit: $%s / Second' % self.shortNum(totalIncome))
        self.itemRate_label.setText('Sales: %s Items / Second' % str(round(totalSales, 2)))

    def frameRateAnalyze(self):
        self.lastFrameRateAnalysisTime = datetime.datetime.now()
        if len(self.frameRateResultSet) > 0:  # Prevent running if frameRateResultSet is empty
            frames = 0
            setpoint = CYCLE_INTERVAL
            target = int(CYCLE_INTERVAL * 1.5)
            high = 0
            highest = 0

            for item in self.frameRateResultSet:
                frames += 1
                if item > target:
                    high += 1
                if item > highest:
                    highest = item

            averageFPS = int(1000 / statistics.mean(self.frameRateResultSet))
            self.frameRateMenuFrame.wids['Frames'].setText(str(frames))
            self.frameRateMenuFrame.wids['Setpoint'].setText(str(setpoint))
            self.frameRateMenuFrame.wids['High Limit'].setText(str(target))
            self.frameRateMenuFrame.wids['High'].setText(str(high) + '%')
            self.frameRateMenuFrame.wids['Highest'].setText(str(highest))
            self.frameRateMenuFrame.wids['AverageFPS'].setText(str(averageFPS))
            self.frameRateMenuFrame.plot()

    def unlockMachine(self, machine):
        if self.balance >= self.machineLib.lib[machine]['unlock']:
            self.updateBalance(self.balance - self.machineLib.lib[machine]['unlock'])
            self.unlockedMachines.append(machine)
            self.buildMenuFrame.wids[machine]['lockImg'].lower()
            self.buildMenuFrame.wids[machine]['lockLabel'].lower()
            self.updateMessage('Unlocked machine type: %s' % machine)
        else:
            self.updateMessage('Not enough money')

    def unlockBlueprint(self, material):
        if self.balance >= self.materialLib.lib[material]['unlock']:
            self.blueprintsMenuFrame.wids[material]['base']['cover'].lower()
            self.blueprintsMenuFrame.wids[material]['base']['lock'].lower()
            self.updateBalance(self.balance - self.materialLib.lib[material]['unlock'])
            self.unlockedBlueprints.append(material)
            self.updateMessage('Unlocked Blueprint: %s' % material)
        else:
            self.updateMessage('Not enough money')

    def unlockResearch(self, option):
        if self.balance >= self.researchLib.lib[option]['cost']:
            self.unlockedResearch.append(option)
            self.updateBalance(self.balance - self.researchLib.lib[option]['cost'])
            self.researchMenuFrame.reset()
            self.updateMessage('Purchased Research for $%s' % self.shortNum(self.researchLib.lib[option]['cost']))
            if self.researchLib.lib[option]['type'] == 'opCostModifier':
                self.opCostModifier = round(self.opCostModifier - 0.4, 1)  # Prevents any slightly off decimals
            elif self.researchLib.lib[option]['type'] == 'maxStarters':
                self.maxStarters = self.maxStarters + self.researchLib.lib[option]['amount']
            elif self.researchLib.lib[option]['type'] == 'maxTeleporters':
                self.maxTeleporters = self.maxTeleporters + self.researchLib.lib[option]['amount']
            elif self.researchLib.lib[option]['type'] == 'opTimeStarterCrafter':
                self.opTimeModifierStarterCrafter = self.opTimeModifierStarterCrafter + 1
            elif self.researchLib.lib[option]['type'] == 'opTimeTier2Machines':
                self.opTimeModifierTier2Machines = self.opTimeModifierTier2Machines + 1
            elif self.researchLib.lib[option]['type'] == 'starterMaxSpawnQuantity':
                self.starterMaxSpawnQuantity = self.starterMaxSpawnQuantity + self.researchLib.lib[option]['amount']
            elif self.researchLib.lib[option]['type'] == 'floorPlanFeature':
                self.floorPlanMenuFrame.reset()
        else:
            self.updateMessage('Not enough money')

    def drawAllArrows(self):
        for tool in self.Machines:
            tool.drawArrow()

    def delAllArrows(self):
        for tool in self.Machines:
            tool.delArrow()

    def delAllHighlights(self):
        for tile in self.Tiles:
            tile.delShape(HIGHLIGHT)

    def getTile(self, x, y):
        for tile in self.Tiles:
            if (tile.x, tile.y) == (x, y):
                return tile
        return None

    def getMachine(self, x, y):
        for tool in self.Machines:
            if (tool.x, tool.y) == (x, y):
                return tool
        return None

    # -------- Generic Methods -------- #

    def convertToSceneCoords(self, xApp, yApp, imgW, imgH):
        xScene = xApp - int(imgW / 2)  # Account for top left image origin, not center
        yScene = yApp + int(imgH / 2) - 1  # Lower by 1px for better visual
        xScene = xScene  # Account for top left scene origin, not bottom left
        yScene = self.sceneHeight - yScene
        return xScene, yScene

    @staticmethod
    def shortNum(n):
        if n < 1000:
            return str(round(n))
        if 1000 <= n < 1000000:
            return str(round(n / 1000, 1)).rstrip('0').rstrip('.') + ' K'
        if 1000000 <= n < 1000000000:
            return str(round(n / 1000000, 1)).rstrip('0').rstrip('.') + ' M'
        if n >= 1000000000:
            return str(round(n / 1000000000, 1)).rstrip('0').rstrip('.') + ' B'

    @staticmethod
    def getTileCenter(x, y):
        xTileCenter = int(((x // 25) * 25) + 13)
        yTileCenter = int(((y // 25) * 25) + 13)
        return xTileCenter, yTileCenter

    @staticmethod
    def getSystemInfo():
        # print('Width =', GetSystemMetrics(0), 'Height =', GetSystemMetrics(1))    # Single monitor
        # print('Width =', GetSystemMetrics(78), 'Height =', GetSystemMetrics(79))  # Combined multi-monitor
        return GetSystemMetrics(0), GetSystemMetrics(1), GetSystemMetrics(78), GetSystemMetrics(79)

    # -------- Robotic Arm Kinematics -------- #

    def precomputeRoboticArmKinematics(self):
        # Compute positions of ends of links AB and BC relative to the tile center at each phase of motion.
        # Compute angles of each link over each phase of motion.
        # Translate position of B and C to centerpoint of link AB and BC by taking average of tile center and B etc.
        # Assume machine defaults to pointing downward, 0 degree angle is towards the right, and image starts at 0 deg.
        # Create secondary sets of positions for tool orientations, U, L, R by taking the positive or negative x and y
        # components from the D orientation & set as appropriate and adding 0, 90, 180, or 270 deg to the link angles.
        # The result is a set of relative positions for AB & BC and absolute angles for thetaAB & thetaBC for each tool
        # orientation and each frame number.

        # Definitions:
        # xRelB, yRelB = Relative position of B
        # xRelC, yRelC = Relative position of C
        # xRelLinkCenterAB, yRelLinkCenterAB = Relative of position of center of link AB
        # xRelLinkCenterBC, yRelLinkCenterBC = Relative of position of center of link BC
        # thetaAB = Angle of link AB
        # thetaBC = Angle of link BC
        # Each term has an associated tool orientation and frame number, ['D'][1], for example.

        # Geometry:
        # Two Linkage Arm = A [=== AB ===] B [=== BC ===] C

        # Variables
        self.thetaAB = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Angle of link AB
        self.thetaBC = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Angle of link BC
        self.xRelB = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative x position of point B (Relative to tool center)
        self.yRelB = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative y position of point B
        self.xRelC = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative x position of point C
        self.yRelC = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative y position of point C

        # Create table of link end points. Assumes tool faces downward by convention
        # Define motion profile by formula for linkage angles at each frame then solve for remaining geometry
        for i in range(1, 13):
            self.thetaAB['D'][i] = 90 + (5 * i)  # Input: Start at 90 deg and inc 60 deg over 12 steps
            self.thetaBC['D'][i] = 90 - (5 * i)  # Input: Start at 90 deg and dec 60 deg over 12 steps
            self.xRelB['D'][i] = self.xArc(12, self.thetaAB['D'][i])
            self.yRelB['D'][i] = self.yArc(12, self.thetaAB['D'][i])
            self.xRelC['D'][i] = self.xRelB['D'][i] + self.xArc(12, self.thetaBC['D'][i])
            self.yRelC['D'][i] = self.yRelB['D'][i] + self.yArc(12, self.thetaBC['D'][i])

        for i in range(13, 37):
            self.thetaAB['D'][i] = 150 + (180 / 24) * (i - 12)  # Input: Start at 150 deg and dec 180 deg over 24 steps
            self.thetaBC['D'][i] = 30 + (180 / 24) * (i - 12)  # Input: Start at 30 deg and inc 180 deg over 24 steps
            self.xRelB['D'][i] = self.xArc(12, self.thetaAB['D'][i])
            self.yRelB['D'][i] = self.yArc(12, self.thetaAB['D'][i])
            self.xRelC['D'][i] = self.xRelB['D'][i] + self.xArc(12, self.thetaBC['D'][i])
            self.yRelC['D'][i] = self.yRelB['D'][i] + self.yArc(12, self.thetaBC['D'][i])

        for i in range(37, 49):
            self.thetaAB['D'][i] = -30 - (60 / 12) * (i - 36)  # Input: Start at -30 deg and dec 60 deg over 12 steps
            self.thetaBC['D'][i] = -150 + (60 / 12) * (i - 36)  # Input: Start at -150 deg and inc 60 deg over 12 steps
            self.xRelB['D'][i] = self.xArc(12, self.thetaAB['D'][i])
            self.yRelB['D'][i] = self.yArc(12, self.thetaAB['D'][i])
            self.xRelC['D'][i] = self.xRelB['D'][i] + self.xArc(12, self.thetaBC['D'][i])
            self.yRelC['D'][i] = self.yRelB['D'][i] + self.yArc(12, self.thetaBC['D'][i])

        # Create tables for remaining tool orientations by multiplying by 1, -1, and/or swapping x and y components
        for i in range(1, 49):
            self.xRelB['U'][i], self.yRelB['U'][i], self.thetaAB['U'][i] = \
                (-self.xRelB['D'][i], -self.yRelB['D'][i], int(self.thetaAB['D'][i] + 180) % 360)
            self.xRelB['L'][i], self.yRelB['L'][i], self.thetaAB['L'][i] = \
                (+self.yRelB['D'][i], -self.xRelB['D'][i], int(self.thetaAB['D'][i] + 270) % 360)
            self.xRelB['D'][i], self.yRelB['D'][i], self.thetaAB['D'][i] = \
                (+self.xRelB['D'][i], +self.yRelB['D'][i], int(self.thetaAB['D'][i] + 0) % 360)
            self.xRelB['R'][i], self.yRelB['R'][i], self.thetaAB['R'][i] = \
                (-self.yRelB['D'][i], +self.xRelB['D'][i], int(self.thetaAB['D'][i] + 90) % 360)

            self.xRelC['U'][i], self.yRelC['U'][i], self.thetaBC['U'][i] = \
                (-self.xRelC['D'][i], -self.yRelC['D'][i], int(self.thetaBC['D'][i] + 180) % 360)
            self.xRelC['L'][i], self.yRelC['L'][i], self.thetaBC['L'][i] = \
                (+self.yRelC['D'][i], -self.xRelC['D'][i], int(self.thetaBC['D'][i] + 270) % 360)
            self.xRelC['D'][i], self.yRelC['D'][i], self.thetaBC['D'][i] = \
                (+self.xRelC['D'][i], +self.yRelC['D'][i], int(self.thetaBC['D'][i] + 0) % 360)
            self.xRelC['R'][i], self.yRelC['R'][i], self.thetaBC['R'][i] = \
                (-self.yRelC['D'][i], +self.xRelC['D'][i], int(self.thetaBC['D'][i] + 90) % 360)

        # Variables for link centers and angles
        self.xRelLinkCenterAB = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative x position of center of link AB
        self.yRelLinkCenterAB = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative y position of center of link AB
        self.xRelLinkCenterBC = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative x position of center of link BC
        self.yRelLinkCenterBC = {'U': {}, 'L': {}, 'D': {}, 'R': {}}  # Relative y position of center of link BC

        # Create table of relative link center positions based on relative end point positions
        for tDir in ['U', 'L', 'D', 'R']:
            for i in range(1, 49):
                self.xRelLinkCenterAB[tDir][i] = int(self.xRelB[tDir][i] / 2)
                self.yRelLinkCenterAB[tDir][i] = int(self.yRelB[tDir][i] / 2)
                self.xRelLinkCenterBC[tDir][i] = int(self.xRelB[tDir][i]
                                                     + (self.xRelC[tDir][i] - self.xRelB[tDir][i]) / 2)
                self.yRelLinkCenterBC[tDir][i] = int(self.yRelB[tDir][i]
                                                     + (self.yRelC[tDir][i] - self.yRelB[tDir][i]) / 2)

        # Create set of Pixmaps at all angles.
        # PyQt defaults to CW so negative makes it CCW to match kinematics convention
        self.angledPixmapLink1 = {}
        for i in range(0, 361):
            self.angledPixmapLink1[i] = QtGui.QPixmap('images/Robotic Arm Link 1.gif')
            transform = QtGui.QTransform().rotate(-i)
            self.angledPixmapLink1[i] = self.angledPixmapLink1[i].transformed(transform, QtCore.Qt.SmoothTransformation)

        self.angledPixmapLink2 = {}
        for i in range(0, 361):
            self.angledPixmapLink2[i] = QtGui.QPixmap('images/Robotic Arm Link 2.gif')
            transform = QtGui.QTransform().rotate(-i)
            self.angledPixmapLink2[i] = self.angledPixmapLink2[i].transformed(transform, QtCore.Qt.SmoothTransformation)

    @staticmethod
    def xArc(radius, angleDeg):
        angleRad = math.radians(angleDeg)
        return int(radius * math.cos(angleRad))

    @staticmethod
    def yArc(radius, angleDeg):
        angleRad = math.radians(angleDeg)
        return int(radius * math.sin(angleRad))

    def getAnyNearbyMaterial(self, piece):
        for material in self.oMaterials:
            if piece.x - 1 <= material.x <= piece.x + 1 and piece.y - 1 <= material.y <= piece.y + 1:
                return material
        return None

    # Material group is None initially and then either join or start their own group upon hitting a roller center
    @staticmethod
    def assignMaterialToNewGroup(material):
        material.group = [material]
        material.groupPos = 0
        material.setGroupVisualOffset(VISUAL_OFFSET_1_TO_2)  # Set offsets and shape will be redrawn next run
        return

    # Set material.group to the existing list by reference and append new material to it. Group list is now shared.
    # Example:
    # material1.group == 0X12345 List Obj
    # material2.group == 0X12345 List Obj
    # List Obj 0X12345 == [material1 obj, material2 obj]
    def assignMaterialToGroup(self, material, joinGroup):
        joinGroup.append(material)
        material.group = joinGroup  # Set .group to reference existing group list
        material.groupPos = self.getFreePosInGroup(joinGroup)
        if len(joinGroup) <= 2:
            offsetList = VISUAL_OFFSET_1_TO_2  # Different offset configs based on group size
        elif len(joinGroup) == 3:
            offsetList = VISUAL_OFFSET_3_TO_3
        elif len(joinGroup) == 4:
            offsetList = VISUAL_OFFSET_4_TO_4
        else:
            offsetList = VISUAL_OFFSET_5_TO_9
        for item in joinGroup:
            item.setGroupVisualOffset(offsetList)  # Shuffle all group positions when a material joins, redraw next run

    @staticmethod
    def getFreePosInGroup(referenceGroup):
        for i in range(0, 99):
            posTakenFlag = False
            for material in referenceGroup:
                if material.groupPos == i:
                    posTakenFlag = True
                    break
            if posTakenFlag is False:
                return i

    def startTimeLog(self):
        self.timeLogEnabled = True

    def stopTimeLog(self):
        self.timeLogEnabled = False
        self.printTimeLog()

    def logTimestamp(self, stampName, runNumber):
        if self.timeLogEnabled:
            self.timeLog.append((stampName, runNumber, time.time()))

    def printTimeLog(self):
        # Error Handling
        if len(self.timeLog) == 0:
            print('No timestamps logged')
            return

        # Get Timestamp Span
        stampName, runNumber, timestamp = self.timeLog[0]
        startTime = timestamp
        startRun = runNumber
        stampName, runNumber, timestamp = self.timeLog[-1]
        endTime = timestamp
        endRun = runNumber
        runSpan = endRun - startRun
        timeSpan = endTime - startTime

        # Build timeLogDicts - Dict (For each run) of dicts containing elapsed times for each timestamp name
        timeLogDicts = {}
        lastTimestamp = None
        for entry in self.timeLog:
            stampName, runNumber, timestamp = entry
            if lastTimestamp is None:
                elapsedTime = 0  # ms
            else:
                elapsedTime = (timestamp - lastTimestamp) * 1000  # ms
            lastTimestamp = timestamp
            if runNumber not in timeLogDicts:
                timeLogDicts[runNumber] = {'Post Start Admin Actions': 0,
                                           'Post Launch Materials': 0,
                                           'Post Move Materials': 0,
                                           'Post Move Robotic Arms': 0,
                                           'Post Material Processing': 0,
                                           'Post End Admin Actions': 0,
                                           'Post Run Idle': 0,
                                           'Row Sum': 0,
                                           'Row Sum w/o Idle': 0}

            timeLogDicts[runNumber][stampName] = elapsedTime

        # Get time sums for each row
        for run in timeLogDicts.keys():
            rowSumColumns = list(timeLogDicts[run].values())[:-2]  # Exclude last columns
            timeLogDicts[run]['Row Sum'] = sum(rowSumColumns)

            rowSumWithoutIdleColumns = list(timeLogDicts[run].values())[:-3]  # Exclude last columns
            timeLogDicts[run]['Row Sum w/o Idle'] = sum(rowSumWithoutIdleColumns)

        # Get maximum times for each stampName
        timeLogDicts['Maximums'] = {}
        for run, runDictionary in timeLogDicts.items():
            for stampName, stampTime in runDictionary.items():
                if stampName not in timeLogDicts['Maximums'] or stampTime > timeLogDicts['Maximums'][stampName]:
                    timeLogDicts['Maximums'][stampName] = stampTime

        # Print Timestamps Table Header
        print('\nStart Timestamps Log:')
        print('Iterations: %i, Timestamps: %i, Spanning: %.1f seconds, UoM: ms'
              % (runSpan, len(self.timeLog), timeSpan))
        print(colored('{:>18}'.format('Iteration'), 'blue'), end='')
        for key in timeLogDicts[startRun].keys():
            print(colored('{:>28}'.format(key), 'blue'), end='')
        print('')

        # Print Timestamp Table Data
        for run, runDictionary in timeLogDicts.items():
            if run == 'Maximums':
                printColor = 'yellow'  # Set print color
                printColorLocked = True
            elif runDictionary['Row Sum'] >= TIME_PROFILE_ALARM_LIMIT:
                printColor = 'red'
                printColorLocked = True
            else:
                printColor = 'grey'
                printColorLocked = False

            # Right aligned with x spaces for col width and d decimals on floating numbers: {:>x.df} = >
            print(colored('{:>18}'.format(run), printColor), end='')
            for value in runDictionary.values():
                if not printColorLocked and value < TIME_PROFILE_ZERO_FLOOR:
                    printColor = 'white'  # Actually darker than 'grey'
                elif not printColorLocked:
                    printColor = 'grey'  # Actually brighter than 'white'
                print(colored('{:>28.3f}'.format(value), printColor), end='')
            print('')

        # Print Timestamps Table Header
        print(colored('{:>18}'.format('Iteration'), 'blue'), end='')
        for key in timeLogDicts[startRun].keys():
            print(colored('{:>28}'.format(key), 'blue'), end='')
        print('')

        # Color Tests
        # print('\n\n\n\nColor Tests:')
        # print(colored(['{:>28.3f}'.format(i) for i in timeLogDict.values()], 'red', attrs=['reverse']))  # Black/Red
        # print(colored(['{:>28.3f}'.format(i) for i in timeLogDict.values()], 'red', 'on_grey'))  # Red/Light Gray
        # print(colored(['{:>28.3f}'.format(i) for i in timeLogDict.values()], 'red'))
        # print(colored(['{:>28.3f}'.format(i) for i in timeLogDict.values()], 'red', attrs=['underline', 'blink']))

        # Clear Recordings
        self.timeLog.clear()
        print('End Timestamps Log\n')


class clsCoreLoop:
    def __init__(self, main):
        self.main = main

    def run(self):
        # Capture prior idle time associate it with prior run
        self.main.logTimestamp('Post Run Idle', self.main.iteration)

        # Increment iteration (Increment at start of run to associate prior idle time at end of run with prior run)
        self.main.iteration += 1

        # Frame rate analysis logging
        iterationToIterationTime = int((datetime.datetime.now() - self.main.iterationStartTime).total_seconds() * 1000)

        # Add frame time to frameRateResultSet list and remove older value
        self.main.frameRateResultSet.append(iterationToIterationTime)
        if len(self.main.frameRateResultSet) > FRAME_RATE_ANALYSIS_LOG_SIZE:
            del self.main.frameRateResultSet[0]

        # Iteration time
        self.main.iterationStartTime = datetime.datetime.now()

        # Get working copies of Machines and Materials to prevent mid iteration changes to lists (Prevents bugs)
        self.main.oMachines = self.main.Machines.copy()
        self.main.oMaterials = self.main.Materials.copy()

        # Money rate analysis
        if (self.main.iterationStartTime - self.main.lastMRAnalysisTime).total_seconds() >= INCOME_ANALYSIS_FREQ:
            self.main.moneyRateAnalyze()

        # Check for achievements
        if self.main.iteration % 10 == 0:  # Achievements check frequency
            self.main.checkAchievements()

        # Fade message & event each loop
        if self.main.iteration - self.main.messageTimer > 40:  # Fade after this many iterations
            self.main.fadeMessage()
        if self.main.iteration - self.main.eventTimer > 40:  # Fade after this many iterations
            self.main.fadeEvent()

        # Remove achievement notification after time limit
        if self.main.iteration - self.main.achievementTimer > 250:  # Fade after this many iterations
            self.main.removeAchievementNotification()

        self.main.logTimestamp('Post Start Admin Actions', self.main.iteration)

        # Check if any machines can launch or transform materials then execute
        if self.main.iteration % MAT_LAUNCH_INTERVAL == 0:  # Only run every x iterations
            for tool in self.main.oMachines:

                # Decrement tool queue timer and create material if timer is up
                if tool.queueDelay > 0:
                    tool.queueDelay -= 1

                # Create material if timer is up
                if tool.queueDelay == 0 and tool.queueMaterial is not None:
                    self.main.Materials.append(clsMaterial(self.main, tool.queueMaterial,
                                                           tool.x, tool.y, tool.orientation,
                                                           tool.starterQuantity))
                    tool.queueMaterial = None

                # Queue any blueprints that can be made
                for blueprint in tool.consideredBlueprints:
                    haveList = tool.contains
                    needList = self.main.materialLib.lib[blueprint]['components']

                    # Check if tool contains blueprint components or no blueprint components required then queue item
                    if self.main.materialLib.lib[blueprint]['components'] == {} or \
                            all(haveList.get(k, 0) >= v for k, v in needList.items()):
                        finalCost = self.main.materialLib.lib[blueprint]['cost'] * self.main.opCostModifier
                        if self.main.balance >= finalCost and tool.queueDelay == 0:

                            # Queue creation of materials
                            tool.queueMaterial = blueprint
                            if tool.type in [STARTER, CRAFTER]:
                                tool.queueDelay = tool.op_time - self.main.opTimeModifierStarterCrafter
                            else:
                                tool.queueDelay = tool.op_time - self.main.opTimeModifierTier2Machines
                            effectiveCost = self.main.materialLib.lib[blueprint]['cost'] * self.main.opCostModifier
                            self.main.updateBalance(self.main.balance - effectiveCost)

                            # Remove blueprint components from container
                            for k, v in self.main.materialLib.lib[blueprint]['components'].items():
                                tool.contains[k] -= v
                            if self.main.selectedMenu == self.main.toolPropertiesFrame \
                                    and tool == self.main.selectedTool:  # Update tool inv menu if displayed
                                self.main.toolPropertiesFrame.refreshInventory()

        self.main.logTimestamp('Post Launch Materials', self.main.iteration)

        # Move each piece of material
        for piece in self.main.oMaterials:
            if piece.pickedUp is False:
                piece.rollerMove()  # Move the piece forward

        self.main.logTimestamp('Post Move Materials', self.main.iteration)

        # Process any motion animations & movements
        for tool in self.main.oMachines:
            if tool.type in [ROBOTIC_ARM, FILTERED_ARM] and tool.motionInProgress is True:
                tool.processArmMovement()

        self.main.logTimestamp('Post Move Robotic Arms', self.main.iteration)

        # Set action for each piece of material
        for piece in self.main.oMaterials:

            if piece.checkIfAtTileCenter():  # Check if on any tool centers

                for tool in self.main.oMachines:
                    if (piece.x, piece.y) == (tool.x, tool.y):  # Material matches a tool center

                        if tool.type in [ROLLER]:
                            piece.orientation = tool.orientation

                            # Group and adjust visual offset for near stacking materials
                            if piece.group is None:
                                nearbyMat = self.main.getAnyNearbyMaterial(piece)
                                # print('Nearby Material Found, Group = %s' % str(nearbyMat.group))

                                if nearbyMat is not None and nearbyMat.group is not None:
                                    self.main.assignMaterialToGroup(piece, nearbyMat.group)
                                else:
                                    # Best to assign group to all mats to prevent further searching
                                    self.main.assignMaterialToNewGroup(piece)

                            # Check for robotic arm pickup off of roller
                            for secondTool in self.main.oMachines:
                                if (piece.x, piece.y) == (secondTool.xPickUpZone, secondTool.yPickUpZone) \
                                        and not piece.pickedUp:
                                    if secondTool.type in [ROBOTIC_ARM, FILTERED_ARM] \
                                            and secondTool.motionInProgress is False:
                                        secondTool.pickUpMaterial(piece)
                                        self.main.updateBalance(
                                            self.main.balance - secondTool.op_cost * self.main.opCostModifier)

                        elif tool.type in [SPLITTER_LEFT, SPLITTER_RIGHT, SPLITTER_TEE, SPLITTER_3WAY]:
                            tool.splitMaterial(piece)
                            self.main.updateBalance(self.main.balance - tool.op_cost * self.main.opCostModifier)

                        elif tool.type in [FILTER_LEFT, FILTER_RIGHT, FILTER_TEE]:
                            tool.filterMaterial(piece)
                            self.main.updateBalance(self.main.balance - tool.op_cost * self.main.opCostModifier)

                        elif tool.type in [TELEPORTER_INPUT]:
                            tool.teleportMaterial(piece)
                            self.main.updateBalance(self.main.balance - tool.op_cost * self.main.opCostModifier)

                        elif tool.type in [CRAFTER, DRAWER, CUTTER, FURNACE, PRESS]:
                            tool.addMaterialToInventory(piece)
                            if self.main.selectedMenu == self.main.toolPropertiesFrame \
                                    and tool == self.main.selectedTool:  # Update tool inv menu if displayed
                                self.main.toolPropertiesFrame.refreshInventory()
                            piece.delMaterial()

                        elif tool.type in [SELLER]:
                            self.main.updateBalance(self.main.balance + piece.value)
                            self.main.updateEvent('Sold %s for $%s!' % (piece.type, self.main.shortNum(piece.value)))
                            for i in range(piece.quantity):  # Account for stacks of material entering machine
                                # Default to 0 then add 1
                                self.main.salesCollector[piece.type] = self.main.salesCollector.get(piece.type, 0) + 1
                            piece.delMaterial()

                        break  # Exit innermost for loop when machine is found

                # Check if material fell off rollers and applicable machines
                piece.onFloor = True
                for tool in self.main.oMachines:
                    if (piece.x, piece.y) == (tool.x, tool.y):  # Material matches tool center
                        if tool.type in [STARTER]:
                            pass  # Materials can't roll across Starters
                        elif tool.type in [FILTERED_ARM, ROBOTIC_ARM]:
                            pass  # Materials fall on floor if on top of robotic arm without being picked up
                        else:
                            piece.onFloor = False
                if piece.onFloor:
                    piece.delMaterial()  # Material is not on machine and is removed

        self.main.logTimestamp('Post Material Processing', self.main.iteration)

        # Check for low balance
        if self.main.balance < 100:
            self.main.updateMessage('Starters may not be able to afford raw materials! May need to sell machines')

        # Check for game reset flag
        if self.main.queueReset:
            self.main.reset()

        self.main.logTimestamp('Post End Admin Actions', self.main.iteration)

        # Core loop runs processes, updates data, and calls scene paint events then PyQt manager processes events
        # and repaints the scene automatically during idle time (after core run loop ends) as quickly as possible.

        # Enable this code section only to manually measure time required to repaint the scene
        # Otherwise application performs better with it off
        # app.processEvents()
        # self.main.logTimestamp('Post Force Events', self.main.iteration)


# -------- Main App Functions -------- #

def exceptHook(type_, value, traceback_):  # Req to return error traceback on PyQt 5.5 including sig/slots
    traceback.print_exception(type_, value, traceback_)
    QtCore.qFatal('')


# -------- Main App -------- #

if __name__ == '__main__':  # Run if main program, but not if imported this from elsewhere
    sys.excepthook = exceptHook  # Req to return error traceback on PyQt 5.5 including sig/slots
    app = QtWidgets.QApplication(sys.argv)
    mainApp = clsMainApp()
    mainApp.finishSetup()
    sys.exit(app.exec_())

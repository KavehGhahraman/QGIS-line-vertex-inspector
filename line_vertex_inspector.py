"""
Line Vertex Inspector Plugin for QGIS
This plugin allows automatic navigation through vertices of a selected line feature
"""

from qgis.PyQt.QtCore import QTimer, Qt
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QSpinBox, QHBoxLayout
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject, QgsWkbTypes, QgsGeometry, QgsRectangle, QgsPointXY
from qgis.gui import QgsMapCanvas
import os

class LineVertexInspector:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.dock_widget = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_to_next_vertex)
        
        self.current_feature = None
        self.vertices = []
        self.current_vertex_index = 0
        self.is_playing = False
        self.current_zoom_scale = None
        
    def initGui(self):
        # Create action for the plugin
        self.action = QAction("Line Vertex Inspector", self.iface.mainWindow())
        self.action.triggered.connect(self.show_dock)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Line Vertex Inspector", self.action)
        
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&Line Vertex Inspector", self.action)
        if self.dock_widget:
            self.iface.removeDockWidget(self.dock_widget)
            
    def show_dock(self):
        if self.dock_widget is None:
            self.create_dock_widget()
        self.dock_widget.show()
        
    def create_dock_widget(self):
        # Create dock widget
        self.dock_widget = QDockWidget("Line Vertex Inspector", self.iface.mainWindow())
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create main widget
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Select a line feature and click Start")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Delay (seconds):")
        from qgis.PyQt.QtWidgets import QDoubleSpinBox
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setMinimum(0.1)
        self.speed_spinbox.setMaximum(10.0)
        self.speed_spinbox.setSingleStep(0.1)
        self.speed_spinbox.setDecimals(1)
        self.speed_spinbox.setValue(1.0)
        self.speed_spinbox.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_spinbox)
        layout.addLayout(speed_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Start")
        self.play_button.clicked.connect(self.start_inspection)
        button_layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_inspection)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_inspection)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Progress label
        self.progress_label = QLabel("")
        layout.addWidget(self.progress_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        self.dock_widget.setWidget(widget)
        
        # Add dock widget to QGIS
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        
    def update_speed(self):
        if self.is_playing:
            self.timer.setInterval(int(self.speed_spinbox.value() * 1000))
            
    def start_inspection(self):
        # Get active layer
        layer = self.iface.activeLayer()
        
        if not layer:
            self.status_label.setText("Error: No active layer")
            return
            
        # Get selected features
        selected = layer.selectedFeatures()
        
        if len(selected) == 0:
            self.status_label.setText("Error: No feature selected")
            return
            
        if len(selected) > 1:
            self.status_label.setText("Error: Please select only ONE line feature")
            return
            
        feature = selected[0]
        geom = feature.geometry()
        
        # Check if it's a line
        if geom.type() != QgsWkbTypes.LineGeometry:
            self.status_label.setText("Error: Selected feature is not a line")
            return
            
        # Store current zoom scale
        self.current_zoom_scale = self.canvas.scale()
        
        # Extract vertices
        self.vertices = []
        if geom.isMultipart():
            for part in geom.asMultiPolyline():
                self.vertices.extend(part)
        else:
            self.vertices = geom.asPolyline()
            
        if len(self.vertices) < 2:
            self.status_label.setText("Error: Line has less than 2 vertices")
            return
            
        # Reset and start
        self.current_vertex_index = 0
        self.current_feature = feature
        self.is_playing = True
        
        # Update UI
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        # Move to first vertex immediately
        self.move_to_next_vertex()
        
        # Start timer for subsequent vertices
        self.timer.start(int(self.speed_spinbox.value() * 1000))
        
    def move_to_next_vertex(self):
        if self.current_vertex_index >= len(self.vertices):
            self.stop_inspection()
            self.status_label.setText("Inspection completed!")
            return
            
        # Get current vertex
        vertex = self.vertices[self.current_vertex_index]
        
        # Update progress
        self.progress_label.setText(f"Vertex {self.current_vertex_index + 1} of {len(self.vertices)}")
        self.status_label.setText(f"Inspecting vertex at: {vertex.x():.2f}, {vertex.y():.2f}")
        
        # Center map on vertex with current zoom scale
        self.canvas.setCenter(vertex)
        self.canvas.zoomScale(self.current_zoom_scale)
        self.canvas.refresh()
        
        # Move to next vertex
        self.current_vertex_index += 1
        
    def pause_inspection(self):
        if self.is_playing:
            self.timer.stop()
            self.is_playing = False
            self.play_button.setText("Resume")
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.status_label.setText("Paused")
        else:
            # Resume
            self.timer.start(int(self.speed_spinbox.value() * 1000))
            self.is_playing = True
            self.play_button.setText("Start")
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            
    def stop_inspection(self):
        self.timer.stop()
        self.is_playing = False
        self.current_vertex_index = 0
        self.vertices = []
        self.current_feature = None
        
        # Reset UI
        self.play_button.setText("Start")
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.progress_label.setText("")
        self.status_label.setText("Select a line feature and click Start")


def classFactory(iface):
    return LineVertexInspector(iface)
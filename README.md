# Line Vertex Inspector

A QGIS plugin to automatically navigate through vertices of selected line features for quality control.

## Features

- Automatic navigation through all vertices of a line feature
- Adjustable speed (0.1 to 10 seconds delay)
- Play/Pause/Stop controls
- Maintains current zoom level
- Real-time progress tracking

## Installation

1. Download or clone this repository
2. Copy the `line_vertex_inspector` folder to your QGIS plugins directory:
   - Windows: `C:\Users\[YourUsername]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - Mac: `/Users/[YourUsername]/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - Linux: `/home/[YourUsername]/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Enable the plugin in Plugins → Manage and Install Plugins → Installed

## Usage

1. Load a line layer in QGIS
2. Select ONE line feature
3. Zoom to your desired inspection level
4. Open the plugin panel: Plugins → Line Vertex Inspector
5. Set the delay between vertices
6. Click "Start" to begin automatic inspection
7. Use Pause/Stop controls as needed

## Requirements

- QGIS 3.0 or higher

## License

MIT License

## Author

Kaveh Ghahraman
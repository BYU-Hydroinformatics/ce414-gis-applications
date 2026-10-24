# Render the per-step ModelBuilder snippets for the Lab 7 page by cutting the two finished models'
# SVG exports (docs/assignments/lab-07/images/lab07-model-hand.svg and lab07-model-floodloop.svg,
# exported from ModelBuilder in ArcGIS Pro 3.7.1) down to the elements one step adds, with their
# inputs and outputs. No ArcGIS Pro session is needed; the cutting is in tools/model_snippets.py.
#
#   "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" tools\lab07\render_model_snippets.py
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from model_snippets import make_snippets

IMAGES = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "assignments", "lab-07", "images"))
HAND = "lab07-model-hand.svg"
LOOP = "lab07-model-floodloop.svg"
SNIPPETS = [
    (HAND, ["Provo_DEM.", "Fill", "Filled_DEM", "Flow ", "Flow_Directi", "Output drop "],
     "lab07-model-step2.png"),
    (HAND, ["Flow_Directi", "Flow @,270", "Flow_Accum", "Threshold", "Raster ", "Stream_Cell"],
     "lab07-model-step3a.png"),
    (HAND, ["Stream_Cell", "Provo_River", "Buffer", "River_Corrid", "Extract by ", "River_Cells"],
     "lab07-model-step3b.png"),
    (HAND, ["Filled_DEM", "Flow_Directi", "River_Cells", "Flow @,256", "HAND"],
     "lab07-model-step4.png"),
    (LOOP, ["Stage_Table", "Iterate Field ", "Value"], "lab07-model-step5a.png"),
    (LOOP, ["Value", "HAND", "Raster ", "flood_%"], "lab07-model-step5b.png"),
    (LOOP, ["flood_%", "Raster to ", "floodpoly_%"], "lab07-model-step5c.png"),
    (LOOP, ["floodpoly_%", "Calculate ", "floodpoly_St"], "lab07-model-step5-calc.png"),
    (LOOP, ["floodpoly_St", "Collect ", "Output ", "Output Table", "Merge", "Floods"],
     "lab07-model-step5d.png"),
]

if __name__ == "__main__":
    make_snippets(IMAGES, SNIPPETS)

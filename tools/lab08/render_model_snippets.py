# Render the per-step ModelBuilder snippets for the Lab 8 page by cutting the finished model's SVG
# export (docs/assignments/lab-08/images/lab08-full-model.svg, exported from ModelBuilder in
# ArcGIS Pro 3.7.1) down to the elements one step adds, with their inputs and outputs. No ArcGIS
# Pro session is needed; the cutting is in tools/model_snippets.py.
#
#   "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" tools\lab08\render_model_snippets.py
#
# The error rasters become parameters only at the end of Step 7, so their P markers are dropped
# from the earlier snippets.
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from model_snippets import make_snippets

IMAGES = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "assignments", "lab-08", "images"))
M = "lab08-full-model.svg"
SNIPPETS = [
    (M, ["Sample ", "Create "], "lab08-model-step2.png"),
    (M, ["Sample ", "Create ", "Thiessen_P"], "lab08-model-step3a.png"),
    (M, ["Thiessen_P", "Polygon to ", "Thiessen_S"], "lab08-model-step3b.png"),
    (M, ["Sample ", "IDW Power", "IDW", "IDW_Surfac"], "lab08-model-step4.png"),
    (M, ["Sample ", "Semivariogr", "Kriging", "Kriging_Surf", "Output "], "lab08-model-step5.png"),
    (M, ["True_DEM", "Thiessen_S", "Raster @548,252", "Error_Thiess"], "lab08-model-step6.png",
     ["Error_Thiess"]),
    (M, ["Error_Thiess", "Raster @749,247", "SqError_Thi"], "lab08-model-step7a.png", ["Error_Thiess"]),
    (M, ["SqError_Thi", "Study_Area", "Zonal @950,247", "RMSE_Thie", "Output Join @1050,277"],
     "lab08-model-step7b.png"),
    (M, ["RMSE_Thie", "Calculate @1151,226", "RMSE @1251,226"], "lab08-model-step7c.png"),
]

if __name__ == "__main__":
    make_snippets(IMAGES, SNIPPETS)

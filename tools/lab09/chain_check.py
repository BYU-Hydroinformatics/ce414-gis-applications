r"""Check the in-model RMSE recipe on the seed-1 baseline tables in C:\Ames\Lab09\Check.gdb:
Calculate Field RMSE = math.sqrt(!MEAN!) on the Zonal Statistics as Table output; and the fields
Zonal Statistics as Table writes."""
import arcpy
arcpy.env.workspace = r"C:\Ames\Lab09\Check.gdb"
for t in ("ZS_Th_n2500_s1", "ZS_IDW_n2500_s1_p2", "ZS_Kr_n2500_s1_SPH"):
    arcpy.management.CalculateField(t, "RMSE", "math.sqrt(!MEAN!)", "PYTHON3", field_type="DOUBLE")
    print(t, [f.name for f in arcpy.ListFields(t)], list(arcpy.da.SearchCursor(t, ["COUNT", "AREA", "MEAN", "RMSE"])))

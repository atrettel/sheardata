import sqlite3
import sheardata as sd
import numpy as np

conn   = sqlite3.connect( "sheardata.db" )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

# TODO: Implement this with uncertainties from the database itself.


fluid_id    = sd.F_LIQUID_WATER
quantity_id = sd.Q_KINEMATIC_VISCOSITY

#pressure    = sd.sdfloat(13789515.0)
#temperature = sd.sdfloat(300.0)

#pressure = sd.sdfloat(4000.0*sd.PASCALS_PER_PSI)
#temperature = sd.sdfloat(sd.ABSOLUTE_ZERO+20.00)

pressure    = sd.sdfloat(sd.STANDARD_ATMOSPHERIC_PRESSURE,0.0)
temperature = sd.sdfloat(sd.ABSOLUTE_ZERO+30.00,0.0)

#pressure    = sd.sdfloat(sd.PASCALS_PER_BAR)
#temperature = sd.sdfloat(sd.ABSOLUTE_ZERO+00.00)

#pressure    = sd.sdfloat(sd.STANDARD_ATMOSPHERIC_PRESSURE,0.0)
#temperature = sd.sdfloat(300.0,0.0)

fluid_property_value = sd.interpolate_fluid_property_value(
    cursor,
    pressure,
    temperature,
    fluid_id,
    quantity_id,
    #citation_key="HaarL+1984+eng+BOOK",
)

print( pressure / sd.STANDARD_ATMOSPHERIC_PRESSURE )
print( temperature - sd.ABSOLUTE_ZERO )
print( fluid_property_value )

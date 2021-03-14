#!/bin/bash

openscad -o "/nameplates/"$1"-NoLogo.stl" -D 'serial="'$1'"' -D "logo=false" "/voron_serial_plate/Voron_Logo_Plate.scad"
openscad -o "/nameplates/"$1".stl" -D 'serial="'$1'"' "/voron_serial_plate/Voron_Logo_Plate.scad"

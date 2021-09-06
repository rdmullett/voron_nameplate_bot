#!/bin/bash

if [[ $1 == V0* ]] ;
then	
openscad -o $2$1"-NoLogo.stl" -D 'serial="'$1'"' -D "logo=false" "/voron_serial_plate/V0/Voron0_Logo_Plate.scad"
openscad -o $2$1".stl" -D 'serial="'$1'"' "/voron_serial_plate/V0/Voron0_Logo_Plate.scad"
else
openscad -o $2$1"-NoLogo.stl" -D 'serial="'$1'"' -D "logo=false" "/voron_serial_plate/Voron_Logo_Plate.scad"
openscad -o $2$1".stl" -D 'serial="'$1'"' "/voron_serial_plate/Voron_Logo_Plate.scad"
fi

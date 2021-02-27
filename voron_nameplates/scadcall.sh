#!/bin/bash
#TODO: change absolute pathing issue after testing
openscad -o "/nameplates/"$1"-NoLogo.stl" -D 'serial="'$1'"' -D "logo=false" "/home/username/voron_serial_plate/Voron_Logo_Plate.scad"
openscad -o "/nameplates/"$1".stl" -D 'serial="'$1'"' "/home/username/voron_serial_plate/Voron_Logo_Plate.scad"

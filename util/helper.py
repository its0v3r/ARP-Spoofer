#!/usr/bin/env python
#
# HELPER FUNCTIONS
#
# Author: Matheus Heidemann
#
# Description: these are generic functions to validate integeres and if the user is running the script as sudo or root
#
# 02 August 2022
#
# Version: 1.0.0
#
# License: MIT License


# IMPORTS
import os


# FUNCTIONS
# Function to validate if the value entered is a integer
def checkNumInt(msg, default_value):
    if default_value:
        try:
            return int(input(msg))
        except ValueError:
            return default_value
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("ERROR! Please enter a valid number (int).\n")
            continue


# Function to validate the YES ir NO response
def checkStringYesOrNo(responseStr, default_value):
    if default_value:
        try:
            strResponse = str(input(responseStr)).upper()
            if strResponse == "Y" or strResponse == "N":
                return strResponse
            else:
                raise ValueError
        except ValueError:
            return default_value
    while True:
        try:
            strResponse = str(input(responseStr)).upper()
            if strResponse == "Y" or strResponse == "N":
                return strResponse
            else:
                raise ValueError
        except ValueError:
            print('Invalid value! Please input "Y" for "YES" or "N" for "NO""!\n')
            continue

# Function to validate if the user is running as sudo or root
def check_privileges():
    if not os.environ.get("SUDO_UID") and os.geteuid() != 0:
        print("You need to run this script with sudo or as root.")
        quit()

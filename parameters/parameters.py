# -*-coding:Utf-8 -*

""" This module contains some global parameters to be changed if needed """

#################################
# Map parameters                #
#################################

# Minimum length of columns and rows a labyrinth must have to be considered valid.
map_min_size = 5

# Maximum length of columns and rows a labyrinth must have to be considered valid.
map_max_size = 100

# Characters authorized in maps
valid_map_items = ['O', 'U', 'X', '.', ' ', '\n']

#################################
# Storage locations             #
#################################

# Directory where the maps are stored
dir_maps = "_data_maps"

# Test directory
dir_test = "test"

# Directory where the test maps are stored within the test directory
dir_test_maps = "_test_data_maps"

#################################
# server parameters             #
#################################

host = ''
port = 12800
client_host = "localhost"

#!/bin/bash

# initial the tables for UTA100 race data
sqlite3 uta_2025.db3 < uta_2025.sql

# assign the write permission to the group user
chmod g+w uta_2025.db3

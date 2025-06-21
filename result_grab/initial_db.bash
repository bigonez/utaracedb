#!/bin/bash

# initial the tables for UTA race data
sqlite3 uta_2025.db3 < uta_2025.sql

# initial the tables for polynomial fitting
sqlite3 uta_2025.db3 < uta_polynomialfit.sql

# assign the write permission to the group user
chmod g+w uta_2025.db3

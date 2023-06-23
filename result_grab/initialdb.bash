#!/bin/bash

# initial the tables for ksphotoflow
sqlite3 uta100_2023.db3 < uta100_2023.sql

# assign the write permission to the group user
chmod g+w uta100_2023.db3

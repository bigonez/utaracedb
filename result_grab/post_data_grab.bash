#!/bin/bash

# dunplicate the database for UTA race data
cp uta_2025.db3 uta_nodes.db3

# assign the write permission to the group user
chmod g+w uta_nodes.db3

# simplify the table struture
sqlite3 uta_nodes.db3 < post_data_grab.sql

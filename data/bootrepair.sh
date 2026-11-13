#!/bin/sh
# BootRepair launcher
exec /usr/bin/python3 -I -c 'import sys; sys.path.insert(0, "/usr/lib/bootrepair"); from bootrepair.app import main; sys.exit(main(["bootrepair"] + sys.argv[1:]))' "$@"

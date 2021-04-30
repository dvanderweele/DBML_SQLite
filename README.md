# DBML to SQLite Utility

This is a simple package built on top of [the PyDBML package by Vanderhoof](https://github.com/Vanderhoof/PyDBML). It allows you, within certain constraints, to generate valid SQLite from `.dbml` files for your Python programs.

## Using the Library

## Writing SQLite Compatible DBML

Not all valid DBML will result in valid SQLite. However, this library attempts to coerce commonly used language in DBML for other SQL flavors to compatible SQLite statements. If this is not possible, an error will be raised. 

For best results, it is recommended to stick to the following valid SQLite types, which are shown next to their corresponding Python types:


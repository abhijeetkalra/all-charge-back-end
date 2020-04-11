#!/bin/bash
coverage run --omit="*/venv/*" tests.py
coverage report

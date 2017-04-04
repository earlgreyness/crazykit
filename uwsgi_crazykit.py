import sys
import os

APP_PATH = '/var/www/crazykit'
sys.path.insert(0, APP_PATH)
os.chdir(APP_PATH)

from app import app as application

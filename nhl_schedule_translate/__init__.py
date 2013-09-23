from flask import Flask
app = Flask(__name__)
import nhl_schedule_translate.views

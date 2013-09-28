from flask import Flask
app = Flask(__name__,  static_url_path='/nhl_static')
import nhl_schedule_translate.views

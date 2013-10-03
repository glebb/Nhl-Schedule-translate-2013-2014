from flask import Flask, session
app = Flask(__name__,  static_url_path='/nhl_static')
app.secret_key = 'xcv823urfjvnsn'
import nhl_schedule_translate.views

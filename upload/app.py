from flask import Flask
import conf

def create_app(config = None):
	print("Creating the app")
	config = conf.init()
	app = Flask(__name__)
	dict.update(app.config,config)
	return app

app = create_app()
#cors = CORS(app, resources={r"/": {"origins": "*"}})


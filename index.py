from flask import Flask
import passgen

app = Flask(__name__)

@app.route('/')
def password():
    return passgen.generate_password()

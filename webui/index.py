import os
from flask import Flask, render_template
app = Flask(__name__)
from dotenv import load_dotenv

#imagedir = "D:\Projects\Discord-RPG\webui\static\images"

load_dotenv()
imagedir = os.getenv('IMAGE_DIR')

file_list = [f for f in os.listdir(imagedir) if f.endswith('.jpeg')]

@app.route("/")
def hello():
    return render_template('index.html', images=file_list)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')
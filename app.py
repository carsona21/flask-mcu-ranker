from flask import Flask, render_template

# If you need anything from main.py, you can import here, for example:
# from main import my_helper_function, mcu_movies

app = Flask(__name__)

@app.route('/')
def index():
    # Render the index.html template in the 'templates' folder
    return render_template('index.html')

if __name__ == '__main__':
    # Start the Flask dev server
    app.run(debug=True)

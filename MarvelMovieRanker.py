from flask import Flask, render_template, request, jsonify, session, url_for
import random
import os
from itertools import combinations
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

# Disable logging of each request
log = logging.getLogger('werkzeug')
log.disabled = True

# List of all MCU movies (up to 2024)
mcu = [
    "Iron Man", "The Incredible Hulk", "Iron Man 2", "Thor", "Captain America: The First Avenger",
    "The Avengers", "Iron Man 3", "Thor: The Dark World", "Captain America: The Winter Soldier",
    "Guardians of the Galaxy", "Avengers: Age of Ultron", "Ant-Man", "Captain America: Civil War",
    "Doctor Strange", "Guardians of the Galaxy Vol. 2", "Spider-Man: Homecoming", "Thor: Ragnarok",
    "Black Panther", "Avengers: Infinity War", "Ant-Man and The Wasp", "Captain Marvel",
    "Avengers: Endgame", "Spider-Man: Far From Home", "Black Widow", "Shang-Chi and the Legend of the Ten Rings",
    "Eternals", "Spider-Man: No Way Home", "Doctor Strange in the Multiverse of Madness",
    "Thor: Love and Thunder", "Black Panther: Wakanda Forever", "Ant-Man and the Wasp: Quantumania",
    "Guardians of the Galaxy Vol. 3", "The Marvels", "Deadpool and Wolverine", "Logan", "X-men days of future past", "Deadpool", "Deadpool 2",
    "The Wolverine", "X-men Apocalypse", "X-men Origins Wolverine", "X-men The Last Stand", "X-2", "Dark Phoenix", "The New Mutants (aka trash)"
]

# Shuffle movies to make initial rankings random
def shuffle_movies():
    random.shuffle(mcu)
    return mcu[:]

@app.route('/')
def index():
    session['movies'] = shuffle_movies()
    session['rankings'] = mcu[:]  # Start with all movies in the ranking
    session['pairs'] = list(combinations(session['movies'], 2))  # Generate all possible pairs
    session['completed_pairs'] = 0

    if session['pairs']:
        session['current_pair'] = random.choice(session['pairs'])
    
    return render_template('rank.html', movie1=session['current_pair'][0], movie2=session['current_pair'][1])

@app.route('/next_pair', methods=['POST'])
def next_pair():
    if len(session['pairs']) == 0:
        return jsonify({'redirect': url_for('results')})

    # Check if request.json exists and contains 'choice'
    chosen = request.json.get('choice')
    if not chosen:
        return jsonify({'error': 'Invalid request'}), 400
    
    movie1, movie2 = session.get('current_pair', (None, None))
    if not movie1 or not movie2:
        return jsonify({'redirect': url_for('results')})

    if chosen == 'movie1':
        session['rankings'].remove(movie2)
    elif chosen == 'movie2':
        session['rankings'].remove(movie1)
    
    # Update pairs
    session['pairs'] = [pair for pair in session['pairs'] if movie1 in pair or movie2 in pair]
    
    # Check if pairs still exist
    if len(session['pairs']) > 0:
        session['current_pair'] = random.choice(session['pairs'])
        movie1, movie2 = session['current_pair']
    else:
        return jsonify({'redirect': url_for('results')})
    
    progress = int(((len(mcu) - len(session['rankings'])) / len(mcu)) * 100)
    return jsonify({'movie1': movie1, 'movie2': movie2, 'progress': progress})


@app.route('/results')
def results():
    return render_template('results.html', rankings=session['rankings'])

# Create basic HTML templates
template_folder = 'templates'
os.makedirs(template_folder, exist_ok=True)

rank_html = """
<!DOCTYPE html>
<html>
<head>
    <title>CarsonsMCU Ranker</title>
    <script>
        function sendChoice(choice) {
            fetch('/next_pair', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ choice: choice })
            })
            .then(response => response.json())
            .then(data => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    document.getElementById('movie1').innerText = data.movie1;
                    document.getElementById('movie2').innerText = data.movie2;
                    document.getElementById('progress').innerText = 'Progress: ' + data.progress + '%';
                }
            });
        }
    </script>
</head>
<body>
    <div>
        <h1>Which do you prefer?</h1>
        <button id="movie1" onclick="sendChoice('movie1')">{{ movie1 }}</button>
        <button id="movie2" onclick="sendChoice('movie2')">{{ movie2 }}</button>
    </div>
    <div id="progress">Progress: 0%</div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

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
    session['rankings'] = []
    session['pairs'] = random.sample(list(combinations(session['movies'], 2)), min(50, len(session['movies']) * 2))  # Limit to 50 pairs max
    session['total_pairs'] = len(session['pairs'])
    session['completed_pairs'] = 0

    if session['pairs']:
        session['current_pair'] = random.choice(session['pairs'])
    
    return render_template('rank.html', movie1=session['current_pair'][0], movie2=session['current_pair'][1])

@app.route('/next_pair', methods=['POST'])
def next_pair():
    if session['completed_pairs'] >= session['total_pairs'] or len(session['pairs']) == 0:
        return jsonify({'redirect': url_for('results')})

    chosen = request.json['choice']
    movie1, movie2 = session['current_pair']

    if chosen == 'movie1':
        session['rankings'].insert(0, movie1)
    elif chosen == 'movie2':
        session['rankings'].insert(0, movie2)
    else:  # 'undecided'
        session['pairs'].append((movie1, movie2))  # Reinsert for later comparison

    session['pairs'].remove((movie1, movie2))
    session['completed_pairs'] += 1

    if len(session['pairs']) > 0:
        session['current_pair'] = random.choice(session['pairs'])
        movie1, movie2 = session['current_pair']
    else:
        return jsonify({'redirect': url_for('results')})

    progress = int((session['completed_pairs'] / session['total_pairs']) * 100)
    return jsonify({'movie1': movie1, 'movie2': movie2, 'progress': progress})

@app.route('/results')
def results():
    unique_rankings = []
    [unique_rankings.append(movie) for movie in session['rankings'] if movie not in unique_rankings]

    missing_movies = [movie for movie in mcu if movie not in unique_rankings]
    unique_rankings.extend(missing_movies)

    return render_template('results.html', rankings=unique_rankings)

# Create basic HTML templates
template_folder = 'templates'
os.makedirs(template_folder, exist_ok=True)

rank_html = """
<!DOCTYPE html>
<html>
<head>
    <title>CarsonsMCU Ranker</title>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/next_pair', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ choice: 'none' })
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
        });

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
    <style>
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .button-container {
            display: flex;
            gap: 20px;
        }
        button {
            font-size: 1.5em;
            padding: 20px;
            cursor: pointer;
            min-width: 300px;
            height: 100px;
            text-align: center;
            white-space: normal;
        }
        .progress {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Which do you prefer?</h1>
        <div class="button-container">
            <button id="movie1" onclick="sendChoice('movie1')">{{ movie1 }}</button>
            <button id="movie2" onclick="sendChoice('movie2')">{{ movie2 }}</button>
            <button onclick="sendChoice('undecided')">I can't decide</button>
        </div>
        <div class="progress" id="progress">Progress: 0%</div>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

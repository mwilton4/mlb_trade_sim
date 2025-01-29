from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)
DB_PATH = "mlb.db"

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def home():
    # Render the main HTML page
    return render_template('index.html')

@app.route('/teams', methods=['GET'])
def get_teams():
    # Query teams table for MLB teams only (parent_team_id is NULL)
    teams = query_db("SELECT team_id, team_name FROM teams WHERE parent_team_id = team_id")
    return jsonify([{"id": row[0], "name": row[1]} for row in teams])

@app.route('/players/<int:team_id>', methods=['GET'])
def get_players(team_id):
    # Query players table for a specific team
    players = query_db("SELECT player_id, player_name, position FROM players WHERE team_id = ?", (team_id,))
    return jsonify([{"id": row[0], "name": row[1], "position": row[2]} for row in players])

if __name__ == '__main__':
    app.run(debug=True)

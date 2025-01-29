# Define tables for players, teams, and trades using SQLAlchemy.



from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)  # e.g., WAR or custom metric

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, nullable=False)
    team2_id = db.Column(db.Integer, nullable=False)
    players_team1 = db.Column(db.String(200), nullable=False)  # Comma-separated
    players_team2 = db.Column(db.String(200), nullable=False)

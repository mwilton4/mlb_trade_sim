import sqlite3
import requests

def fetch_and_store_mlb_teams_and_affiliates(db_path="mlb.db"):
    """
    Fetches all MLB teams, their minor league affiliates, and each affiliate's roster,
    then stores them in a SQLite database.
    
    :param db_path: The path to the SQLite database file.
    """
    # 1. Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Create/alter tables to ensure we have the necessary schema
    create_tables(cursor)

    # 3. Get the list of MLB teams (sportId=1 => MLB)
    mlb_teams_url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
    mlb_teams = requests.get(mlb_teams_url).json().get("teams", [])

    for team in mlb_teams:
        mlb_team_id = team.get("id")
        mlb_team_name = team.get("name")
        mlb_team_loc = team.get("locationName", "")
        mlb_team_abbr = team.get("abbreviation", "")

        # 4. Insert the MLB team as a "team" record
        insert_team(cursor,
                    team_id=mlb_team_id,
                    team_name=mlb_team_name,
                    location_name=mlb_team_loc,
                    abbreviation=mlb_team_abbr,
                    parent_team_id=None)  # MLB teams don't have a parent

        # Optional: If you also want to pull the **MLB** roster for this team
        # fetch_and_store_roster_for_team(cursor, mlb_team_id)

        # 5. Fetch the minor league affiliates for this MLB team
        fetch_and_store_affiliates_for_team(cursor, mlb_team_id)

    # Commit & close
    conn.commit()
    conn.close()
    print(f"All MLB teams and their affiliates (and affiliate rosters) saved to '{db_path}'!")


def fetch_and_store_affiliates_for_team(cursor, mlb_team_id):
    """
    Given an MLB team_id, fetch the minor league affiliates and their rosters.
    """
    # Endpoint to get affiliates: /api/v1/teams/affiliates?teamId=XYZ
    url = f"https://statsapi.mlb.com/api/v1/teams/affiliates?teamIds={mlb_team_id}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch affiliates for team {mlb_team_id}: {e}")
        return

    data = resp.json()
    affiliates = data.get("teams", [])

    for affiliate in affiliates:
        affiliate_id = affiliate.get("id")
        affiliate_name = affiliate.get("name")
        affiliate_loc = affiliate.get("locationName", "")
        affiliate_abbr = affiliate.get("abbreviation", "")

        # Insert or update this affiliate in the 'teams' table;
        # use the MLB team ID as 'parent_team_id'
        insert_team(cursor,
                    team_id=affiliate_id,
                    team_name=affiliate_name,
                    location_name=affiliate_loc,
                    abbreviation=affiliate_abbr,
                    parent_team_id=mlb_team_id)

        # Now fetch roster for the affiliate team
        fetch_and_store_roster_for_team(cursor, affiliate_id)


def fetch_and_store_roster_for_team(cursor, team_id):
    """
    Given a team_id (MLB or MiLB), fetch the roster and store each player.
    """
    roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
    try:
        roster_resp = requests.get(roster_url)
        roster_resp.raise_for_status()
        roster_data = roster_resp.json().get("roster", [])
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch roster for team {team_id}: {e}")
        return

    for player_obj in roster_data:
        person = player_obj.get("person", {})
        position_obj = player_obj.get("position", {})

        player_id = person.get("id")
        player_name = person.get("fullName")
        jersey_number = player_obj.get("jerseyNumber")   # can be None/empty
        position = position_obj.get("abbreviation", "")  # e.g. "P", "C", "1B"

        insert_player(cursor,
                      player_id=player_id,
                      player_name=player_name,
                      jersey_number=jersey_number,
                      position=position,
                      team_id=team_id)


def create_tables(cursor):
    """
    Create or update the schema:
      - 'teams' for both MLB and MiLB
      - 'players' for all players
    """
    # Create teams table (with parent_team_id to link affiliates -> MLB)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT,
            location_name TEXT,
            abbreviation TEXT,
            parent_team_id INTEGER
        )
    """)

    # Create players table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT,
            jersey_number TEXT,
            position TEXT,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
    """)


def insert_team(cursor, team_id, team_name, location_name, abbreviation, parent_team_id=None):
    """
    Inserts or replaces a team (MLB or MiLB affiliate) in the 'teams' table.
    """
    cursor.execute("""
        INSERT OR REPLACE INTO teams (team_id, team_name, location_name, abbreviation, parent_team_id)
        VALUES (?, ?, ?, ?, ?)
    """, (team_id, team_name, location_name, abbreviation, parent_team_id))


def insert_player(cursor, player_id, player_name, jersey_number, position, team_id):
    """
    Inserts or replaces a player into the 'players' table.
    """
    cursor.execute("""
        INSERT OR REPLACE INTO players (
            player_id, player_name, jersey_number, position, team_id
        )
        VALUES (?, ?, ?, ?, ?)
    """, (player_id, player_name, jersey_number, position, team_id))




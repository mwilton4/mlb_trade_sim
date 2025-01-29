from data_utils import save_teams_to_db, save_players_to_db

def update_data():
    save_teams_to_db()
    save_players_to_db()

if __name__ == '__main__':
    update_data()

# Evaluate trade proposals by comparing player values and team needs.

def evaluate_trade(players_team1, players_team2, team1_budget, team2_budget):
    value_team1 = sum(player['value'] for player in players_team1)
    value_team2 = sum(player['value'] for player in players_team2)
    
    if abs(value_team1 - value_team2) > 5:
        return {"status": "rejected", "reason": "Unbalanced trade"}
    
    if any(player['salary'] > team1_budget for player in players_team2) or \
       any(player['salary'] > team2_budget for player in players_team1):
        return {"status": "rejected", "reason": "Budget exceeded"}
    
    return {"status": "approved"}



# League Deletion Documentation

## Overview

League deletion is a commissioner-only operation that removes a league and all associated data including games, props, answers, player selections, and players.

## Endpoint

**POST** `/delete_league`

**Controller**: `leagueController.py:106-113`

**Service**: `leagueService.py:277-319`

---

## Request Format

```http
POST /delete_league HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "leaguename": "My League"
}
```

**Parameters**:
- `leaguename` (string, required): Name of the league to delete

---

## Response Format

**Success** (200):
```json
{
  "message": "League 'My League' and all associated data deleted successfully."
}
```

**Error** (400):
```json
{
  "error": "League name is required"
}
```

**Error** (404):
```json
{
  "error": "League not found"
}
```

---

## Deletion Flow

The `delete_league` service method performs cascading deletion in this order:

### 1. Delete All Games (lines 300-301)

For each game in the league, calls `delete_game()` which:

**Step 1: Delete Winner/Loser Props** (lines 240-250)
- Deletes all `WinnerLoserAnswer` records for each prop
- Deletes all `WinnerLoserProp` records

**Step 2: Delete Over/Under Props** (lines 252-262)
- Deletes all `OverUnderAnswer` records for each prop
- Deletes all `OverUnderProp` records

**Step 3: Delete Variable Option Props** (lines 264-274)
- Deletes all `VariableOptionAnswer` records for each prop
- Deletes all `VariableOptionProp` records

**Step 4: Delete Player Prop Selections** (lines 276-280)
- Deletes all `PlayerPropSelection` records for the game
- **CRITICAL**: This step was added to fix foreign key constraint violations
- Players select which optional props to answer; these selections must be deleted before the game

**Step 5: Delete Game** (lines 282-284)
- Finally deletes the `Game` record itself

### 2. Clear Commissioner Reference (lines 303-305)

```python
league.commissioner_id = None
db.session.flush()
```

Removes the foreign key to the commissioner player to avoid circular dependency issues.

### 3. Delete All Players (lines 307-308)

For each player in the league, calls `delete_player()` which:
- Removes the player from all associated games
- Deletes the `Player` record

### 4. Delete League (lines 310-311)

```python
db.session.delete(league)
db.session.commit()
```

Finally deletes the `League` record itself.

---

## Database Relationships

### Cascade Delete Order

**Critical**: Deletion must follow this order to avoid foreign key violations:

```
League
├── Games (for each game):
│   ├── WinnerLoserAnswers
│   ├── WinnerLoserProps
│   ├── OverUnderAnswers
│   ├── OverUnderProps
│   ├── VariableOptionAnswers
│   ├── VariableOptionProps
│   ├── PlayerPropSelections  ← MUST delete before Game
│   └── Game
├── Commissioner Reference (clear first)
├── Players
└── League
```

---

## Known Issues & Fixes

### Foreign Key Constraint Violation (FIXED)

**Issue**: Delete league failed with error:
```
psycopg2.errors.ForeignKeyViolation: update or delete on table "game"
violates foreign key constraint "player_prop_selection_game_id_fkey"
on table "player_prop_selection"
```

**Root Cause**: `PlayerPropSelection` records were not being deleted before deleting the game.

**Fix** (leagueService.py:276-280):
```python
# Delete all player prop selections for this game
playerPropSelections = PlayerPropSelection.query.filter_by(game_id=game_id).all()
for selection in playerPropSelections:
    db.session.delete(selection)
    db.session.commit()
```

**Date Fixed**: January 2026

---

## Code References

### Controller

**File**: `app/controllers/leagueController.py:106-113`

```python
@leagueController.route('/delete_league', methods=['POST'])
def deleteLeague():
    data = request.get_json()
    leaguename = data.get('leaguename')

    result = LeagueService.delete_league(leaguename)

    return jsonify(result)
```

### Service

**File**: `app/services/leagueService.py:277-319`

**Delete Game Method** (lines 212-284):
```python
@staticmethod
def delete_game(leagueName, game_id):
    # Validate inputs
    leagueName = validate_league_name(leagueName)
    game_id = validate_game_id(game_id)

    league = get_league_by_name(leagueName)
    validate_league_exists(league)

    game = get_game_by_id(game_id)
    validate_game_exists(game)

    # Delete winner/loser props and answers
    for winnerLoserProp in game.winner_loser_props:
        winnerLoserAnswers = WinnerLoserAnswer.query.filter_by(prop_id=winnerLoserProp.id).all()
        for answer in winnerLoserAnswers:
            db.session.delete(answer)
            db.session.commit()
        db.session.delete(winnerLoserProp)
        db.session.commit()

    # Delete over/under props and answers
    for overUnderProp in game.over_under_props:
        overUnderAnswers = OverUnderAnswer.query.filter_by(prop_id=overUnderProp.id).all()
        for answer in overUnderAnswers:
            db.session.delete(answer)
            db.session.commit()
        db.session.delete(overUnderProp)
        db.session.commit()

    # Delete variable option props and answers
    for variableOptionProp in game.variable_option_props:
        variableOptionAnswers = VariableOptionAnswer.query.filter_by(prop_id=variableOptionProp.id).all()
        for answer in variableOptionAnswers:
            db.session.delete(answer)
            db.session.commit()
        db.session.delete(variableOptionProp)
        db.session.commit()

    # Delete all player prop selections for this game
    playerPropSelections = PlayerPropSelection.query.filter_by(game_id=game_id).all()
    for selection in playerPropSelections:
        db.session.delete(selection)
        db.session.commit()

    # Finally, delete the game
    db.session.delete(game)
    db.session.commit()
```

**Delete League Method** (lines 277-319):
```python
@staticmethod
def delete_league(leagueName):
    leagueName = validate_league_name(leagueName)

    league = get_league_by_name(leagueName)
    validate_league_exists(league)

    # Delete all games (cascades to props and answers)
    for game in league.league_games:
        LeagueService.delete_game(leagueName, game.id)

    # Clear commissioner reference to avoid circular dependency
    league.commissioner_id = None
    db.session.flush()

    # Delete all players
    for player in league.league_players:
        LeagueService.delete_player(player.name, leagueName)

    # Delete the league
    db.session.delete(league)
    db.session.commit()

    return {"message": f"League '{leagueName}' and all associated data deleted successfully."}
```

---

## Required Imports

**File**: `app/services/leagueService.py:1-16`

```python
from flask import abort
from app import db
from app.models.leagueModel import League
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer
from app.models.playerPropSelection import PlayerPropSelection
from app.repositories.leagueRepository import get_all_leagues, get_league_by_name, get_leagues_by_username, get_league_by_join_code
from app.repositories.playerRepository import get_player_by_username_and_leaguename, get_player_by_playername_and_leaguename
from app.repositories.gameRepository import get_game_by_id
from app.services.playerService import PlayerService
from app.validators.leagueValidator import validate_league_name, validate_league_exists, validate_join_code, validate_player_name, validate_player_exists
from app.validators.userValidator import validate_username, validate_user_exists
from app.validators.gameValidator import validate_game_exists, validate_game_id
import secrets
import string
```

**Key Imports for Delete Operations**:
- `VariableOptionAnswer` (line 6)
- `PlayerPropSelection` (line 7)

---

## Testing

### Manual Test

1. Create a test league with games
2. Create games with all prop types
3. Have players answer props and select optional props
4. Call `/delete_league` with the league name
5. Verify all data is deleted from database

### Verification Queries

```sql
-- Check league deleted
SELECT * FROM league WHERE name = 'Test League';

-- Check games deleted
SELECT * FROM game WHERE league_id = <league_id>;

-- Check props deleted
SELECT * FROM winner_loser_prop WHERE game_id IN (SELECT id FROM game WHERE league_id = <league_id>);
SELECT * FROM over_under_prop WHERE game_id IN (SELECT id FROM game WHERE league_id = <league_id>);
SELECT * FROM variable_option_prop WHERE game_id IN (SELECT id FROM game WHERE league_id = <league_id>);

-- Check answers deleted
SELECT * FROM winner_loser_answer WHERE prop_id IN (SELECT id FROM winner_loser_prop WHERE game_id IN (SELECT id FROM game WHERE league_id = <league_id>));

-- Check player prop selections deleted
SELECT * FROM player_prop_selection WHERE game_id IN (SELECT id FROM game WHERE league_id = <league_id>);

-- Check players deleted
SELECT * FROM player WHERE league_id = <league_id>;
```

All queries should return 0 rows.

---

## Security Considerations

1. **Authorization**: Only the league commissioner should be able to delete a league
2. **Confirmation**: Consider adding a confirmation step before deletion (frontend)
3. **Soft Delete**: Consider implementing soft delete (mark as deleted instead of hard delete) for data recovery
4. **Audit Log**: Log all league deletions with timestamp and user

---

## Performance Considerations

- Deletion is a heavy operation (many cascading deletes)
- For large leagues with many games/players, this may take several seconds
- Consider implementing a background job for deletion
- Add progress indicator in frontend

---

## Related Documentation

- [League Creation](./league-create.md) - Creating leagues
- [Game Creation](./game-create.md) - Creating games within leagues
- [Player Prop Selection](./prop-selection.md) - How prop selections work

---

*Last Updated: January 2026*

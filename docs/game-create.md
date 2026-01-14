# Create Game Workflow

## Overview

Creating a game involves setting up a new event within a league with associated props (questions) for players to answer. Games can include Winner/Loser props, Over/Under props, and Variable Option props.

## Architecture

```
Frontend Form → POST /create_game → GameService.create_game()
    → Create Game Record
    → Create Winner/Loser Props
    → Create Over/Under Props
    → Create Variable Option Props
    → Return Success
```

## Endpoint

**POST** `/create_game`

**Controller**: `leagueController.py:134-162`

**Service**: `gameService.py:226-286` (`GameService.create_game`)

**Authentication**: Required (session)

---

## Request Format

### Request Body

```json
{
  "leagueName": "My NFL League",
  "gameName": "Los Angeles Rams @ Carolina Panthers",
  "date": "2026-01-29T21:30:00.000Z",
  "externalGameId": "401547638",
  "propLimit": 2,
  "winnerLoserQuestions": [
    {
      "question": "Who will win?",
      "favoriteTeam": "Los Angeles Rams",
      "underdogTeam": "Carolina Panthers",
      "favoritePoints": 1.0,
      "underdogPoints": 2.0,
      "favoriteTeamId": "LA",
      "underdogTeamId": "CAR",
      "is_mandatory": true
    }
  ],
  "overUnderQuestions": [
    {
      "question": "QB Passing Yards O/U 250.5",
      "overPoints": 1.5,
      "underPoints": 1.5,
      "playerName": "Matthew Stafford",
      "playerId": "12483",
      "statType": "passing_yards",
      "lineValue": 250.5,
      "is_mandatory": false
    }
  ],
  "variableOptionQuestions": [
    {
      "question": "Who will score first?",
      "options": [
        { "choice_text": "Rams", "points": 1.5 },
        { "choice_text": "Panthers", "points": 1.5 },
        { "choice_text": "Neither (No score)", "points": 3.0 }
      ],
      "is_mandatory": false
    }
  ]
}
```

### Required Fields

- `leagueName` (string): Name of the league to create game in
- `gameName` (string): Name/description of the game
- `date` (string, ISO 8601): Start time of the game
- `winnerLoserQuestions` (array): At least one Winner/Loser prop
- `overUnderQuestions` (array): Over/Under props (can be empty)
- `variableOptionQuestions` (array): Multiple choice props (can be empty)

### Optional Fields

- `externalGameId` (string): ESPN game ID for live stat polling
- `propLimit` (integer, default: 2): Number of optional props players must select

---

## Response Format

### Success Response (200)

```json
{
  "message": "Created game successfully."
}
```

### Error Response (400/401/404)

```json
{
  "description": "League not found"
}
```

**Possible Error Messages**:
- "League not found" (404)
- "Invalid league name" (400)
- "Game name is required" (400)
- "Start time is required" (400)

---

## Code Flow

### 1. Controller Layer

**File**: `app/controllers/leagueController.py:134-162`

```python
@leagueController.route('/create_game', methods=['POST'])
def createGame():
    data = request.get_json()
    leagueName = data.get('leagueName')
    gameName = data.get('gameName')
    date = data.get('date')
    externalGameId = data.get('externalGameId')  # ESPN game ID
    propLimit = data.get('propLimit', 2)  # Default to 2
    winnerLoserQuestions = data.get('winnerLoserQuestions')
    overUnderQuestions = data.get('overUnderQuestions')
    variableOptionQuestions = data.get('variableOptionQuestions')

    result = GameService.create_game(
        leagueName, gameName, date,
        winnerLoserQuestions, overUnderQuestions, variableOptionQuestions,
        externalGameId, propLimit
    )

    return jsonify(result)
```

### 2. Service Layer

**File**: `app/services/game/gameService.py:226-286`

```python
@staticmethod
def create_game(leagueName, gameName, date, winnerLoserQuestions,
                overUnderQuestions, variableOptionQuestions,
                externalGameId=None, propLimit=2):
    # 1. Get the league
    league = get_league_by_name(leagueName)
    if (league is None):
        abort(401, "League not found")

    # 2. Create game record
    new_game = Game(
        league_id = league.id,
        game_name = gameName,
        start_time = date,
        graded = 0,
        external_game_id = externalGameId,
        prop_limit = propLimit
    )
    db.session.add(new_game)
    db.session.commit()

    # 3. Create all props for the game
    for winnerLoserProp in winnerLoserQuestions:
        GameService.createWinnerLoserQuestion(winnerLoserProp, new_game.id)

    for overUnderProp in overUnderQuestions:
        GameService.createOverUnderQuestion(overUnderProp, new_game.id)

    for variableOptionProp in variableOptionQuestions:
        GameService.createVariableOptionQuestion(variableOptionProp, new_game.id)

    # 4. Add game to league's game list
    league.league_games.append(new_game)
    db.session.commit()

    return {"message": "Created game successfully."}
```

### 3. Prop Creation

#### Winner/Loser Prop

**File**: `app/services/game/gameService.py:334-380`

```python
@staticmethod
def createWinnerLoserQuestion(winnerLoserProp, game_id):
    question = winnerLoserProp.get("question")
    favoritePoints = winnerLoserProp.get("favoritePoints")
    underdogPoints = winnerLoserProp.get("underdogPoints")
    favoriteTeam = winnerLoserProp.get("favoriteTeam")
    underdogTeam = winnerLoserProp.get("underdogTeam")
    favoriteTeamId = winnerLoserProp.get("favoriteTeamId")
    underdogTeamId = winnerLoserProp.get("underdogTeamId")
    is_mandatory = winnerLoserProp.get("is_mandatory", True)

    new_prop = WinnerLoserProp(
        game_id = game_id,
        question = question,
        favorite_points = favoritePoints,
        underdog_points = underdogPoints,
        favorite_team = favoriteTeam,
        underdog_team = underdogTeam,
        team_a_id = favoriteTeamId,
        team_b_id = underdogTeamId,
        team_a_name = favoriteTeam,
        team_b_name = underdogTeam,
        is_mandatory = is_mandatory
    )

    game.winner_loser_props.append(new_prop)
    db.session.add(new_prop)
    db.session.commit()

    return {"message": "Created winner/loser prop successfully."}
```

#### Over/Under Prop

**File**: `app/services/game/gameService.py:383-423`

```python
@staticmethod
def createOverUnderQuestion(overUnderProp, game_id):
    question = overUnderProp.get("question")
    overPoints = overUnderProp.get("overPoints")
    underPoints = overUnderProp.get("underPoints")
    playerName = overUnderProp.get("playerName")
    playerId = overUnderProp.get("playerId")
    statType = overUnderProp.get("statType")
    lineValue = overUnderProp.get("lineValue")
    is_mandatory = overUnderProp.get("is_mandatory", False)

    new_prop = OverUnderProp(
        game_id = game_id,
        question = question,
        over_points = overPoints,
        under_points = underPoints,
        player_name = playerName,
        player_id = playerId,
        stat_type = statType,
        line_value = lineValue,
        is_mandatory = is_mandatory
    )

    game.over_under_props.append(new_prop)
    db.session.add(new_prop)
    db.session.commit()

    return {"message": "Created over/under prop successfully."}
```

#### Variable Option Prop

**File**: `app/services/game/gameService.py:289-332`

```python
@staticmethod
def createVariableOptionQuestion(variableOptionProp, game_id):
    question = variableOptionProp.get("question")
    options = variableOptionProp.get("options")
    is_mandatory = variableOptionProp.get("is_mandatory", False)

    new_prop = VariableOptionProp(
        game_id = game_id,
        question = question,
        is_mandatory = is_mandatory
    )

    new_prop.options = []
    game.variable_option_props.append(new_prop)

    # Create HashMapAnswers for each option
    for option in options:
        new_choice = HashMapAnswers(
            answer_choice = option.get('choice_text'),
            answer_points = option.get('points')
        )
        db.session.add(new_choice)
        new_prop.options.append(new_choice)

    db.session.add(new_prop)
    db.session.commit()
    return {"message": "Created prop successfully."}
```

---

## Database Schema

### Game Model

**File**: `app/models/gameModel.py`

```python
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    game_name = db.Column(db.String(128))
    start_time = db.Column(db.DateTime)
    graded = db.Column(db.Integer, default=0)
    external_game_id = db.Column(db.String(50), nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    prop_limit = db.Column(db.Integer, default=2, nullable=False)

    # Relationships
    winner_loser_props = db.relationship('WinnerLoserProp', ...)
    over_under_props = db.relationship('OverUnderProp', ...)
    variable_option_props = db.relationship('VariableOptionProp', ...)
```

### Winner/Loser Prop Model

**File**: `app/models/props/winnerLoserProp.py`

```python
class WinnerLoserProp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    question = db.Column(db.String(256))
    favorite_team = db.Column(db.String(128))
    underdog_team = db.Column(db.String(128))
    favorite_points = db.Column(db.Float)
    underdog_points = db.Column(db.Float)
    correct_answer = db.Column(db.String(128), nullable=True)
    team_a_id = db.Column(db.String(50), nullable=True)
    team_b_id = db.Column(db.String(50), nullable=True)
    team_a_score = db.Column(db.Integer, nullable=True)
    team_b_score = db.Column(db.Integer, nullable=True)
    is_mandatory = db.Column(db.Boolean, default=True, nullable=False)
```

### Over/Under Prop Model

**File**: `app/models/props/overUnderProp.py`

```python
class OverUnderProp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    question = db.Column(db.String(256))
    over_points = db.Column(db.Float)
    under_points = db.Column(db.Float)
    correct_answer = db.Column(db.String(128), nullable=True)
    player_name = db.Column(db.String(128), nullable=True)
    player_id = db.Column(db.String(50), nullable=True)
    stat_type = db.Column(db.String(50), nullable=True)
    line_value = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, nullable=True)
    is_mandatory = db.Column(db.Boolean, default=False, nullable=False)
```

### Variable Option Prop Model

**File**: `app/models/props/variableOptionProp.py`

```python
class VariableOptionProp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    question = db.Column(db.String(256))
    correct_answer = db.Column(ARRAY(db.String), nullable=True)
    is_mandatory = db.Column(db.Boolean, default=False, nullable=False)

    # Relationship to answer options
    options = db.relationship('HashMapAnswers', ...)
```

---

## Frontend Integration Example

```javascript
const createGame = async () => {
  const gameData = {
    leagueName: "Test League",
    gameName: "Rams @ Panthers",
    date: new Date("2026-01-29T21:30:00").toISOString(),
    externalGameId: "401547638",
    propLimit: 2,
    winnerLoserQuestions: [
      {
        question: "Who will win?",
        favoriteTeam: "Los Angeles Rams",
        underdogTeam: "Carolina Panthers",
        favoritePoints: 1.0,
        underdogPoints: 2.0,
        favoriteTeamId: "LA",
        underdogTeamId: "CAR",
        is_mandatory: true
      }
    ],
    overUnderQuestions: [
      {
        question: "Matthew Stafford Passing Yards O/U 250.5",
        overPoints: 1.5,
        underPoints: 1.5,
        playerName: "Matthew Stafford",
        playerId: "12483",
        statType: "passing_yards",
        lineValue: 250.5,
        is_mandatory: false
      }
    ],
    variableOptionQuestions: []
  };

  const response = await fetch('http://localhost:5000/create_game', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',  // Include session cookie
    body: JSON.stringify(gameData)
  });

  if (response.ok) {
    const result = await response.json();
    console.log(result.message);  // "Created game successfully."
  } else {
    const error = await response.json();
    console.error(error.description);
  }
};
```

---

## Prop Types Explained

### Winner/Loser Props

**Purpose**: Players pick which team will win

**Fields**:
- `question`: Display text (e.g., "Who will win?")
- `favoriteTeam`: Expected winner (lower points)
- `underdogTeam`: Underdog (higher points)
- `favoritePoints`: Points for picking favorite
- `underdogPoints`: Points for picking underdog
- `favoriteTeamId`: ESPN team ID (optional, for live stats)
- `underdogTeamId`: ESPN team ID (optional, for live stats)
- `is_mandatory`: If true, all players must answer this prop

**Default**: Winner/Loser props default to `is_mandatory=True`

### Over/Under Props

**Purpose**: Players pick if a stat will be over or under a threshold

**Fields**:
- `question`: Display text (e.g., "Passing Yards O/U 250.5")
- `overPoints`: Points for picking "over"
- `underPoints`: Points for picking "under"
- `lineValue`: The threshold value (e.g., 250.5)
- `playerName`: Player name (optional, for live stats)
- `playerId`: ESPN player ID (optional, for live stats)
- `statType`: Stat to track (e.g., "passing_yards")
- `is_mandatory`: If true, all players must answer this prop

**Stat Types**:
- `passing_yards`
- `passing_tds`
- `passing_interceptions`
- `rushing_yards`
- `rushing_tds`
- `receiving_yards`
- `receiving_tds`
- `receiving_receptions`
- `scrimmage_yards` (rushing + receiving)

**Default**: Over/Under props default to `is_mandatory=False`

### Variable Option Props

**Purpose**: Multiple choice questions with custom options

**Fields**:
- `question`: Display text
- `options`: Array of choices with point values
  - `choice_text`: Option text
  - `points`: Points awarded for this choice
- `is_mandatory`: If true, all players must answer this prop

**Example Use Cases**:
- "Who will score first?" (Team A, Team B, Neither)
- "Total sacks in game?" (0-1, 2-3, 4-5, 6+)
- "Margin of victory?" (1-7, 8-14, 15+)

**Default**: Variable Option props default to `is_mandatory=False`

---

## Prop Limit Feature

**Field**: `propLimit` (integer, default: 2)

**Purpose**: Determines how many optional props players must select from the pool

**Behavior**:
- Mandatory props are always required (not counted toward limit)
- Optional props are shown in a selection modal
- Players must select exactly `propLimit` optional props
- Players can only answer the props they selected

**Example**:
- Game has 1 mandatory Winner/Loser prop + 4 optional Over/Under props
- `propLimit = 2`
- Player must answer:
  - The 1 mandatory prop (always required)
  - 2 out of the 4 optional props (player's choice)

---

## Common Errors

### 1. League Not Found

**Error**: "League not found" (404)

**Cause**: League name doesn't exist in database

**Solution**: Verify `leagueName` is correct and league exists

---

### 2. Missing Required Fields

**Error**: Various validation errors

**Cause**: Required fields not provided in request

**Solution**: Ensure all required fields are present:
- `leagueName`
- `gameName`
- `date`
- At least one prop in `winnerLoserQuestions`, `overUnderQuestions`, or `variableOptionQuestions`

---

### 3. Invalid Date Format

**Error**: Database error or validation error

**Cause**: Date not in ISO 8601 format

**Solution**: Use `new Date().toISOString()` in frontend:
```javascript
date: new Date("2026-01-29T21:30:00").toISOString()
// Result: "2026-01-29T21:30:00.000Z"
```

---

### 4. Duplicate Game Names

**Note**: Game names are NOT unique - multiple games can have the same name

**This is intentional**: Allows creating multiple games for same matchup

---

### 5. Variable Option Without Options

**Error**: Prop created but no choices available

**Cause**: `options` array is empty or missing

**Solution**: Ensure at least 2 options in `options` array

---

## Validation Rules

### Game Level

- `gameName`: Required, string
- `date`: Required, ISO 8601 datetime
- `leagueName`: Required, must exist in database
- `propLimit`: Optional, integer, min=1, defaults to 2

### Winner/Loser Prop

- `question`: Required, string
- `favoriteTeam`: Required, string
- `underdogTeam`: Required, string
- `favoritePoints`: Required, float
- `underdogPoints`: Required, float
- `is_mandatory`: Optional, boolean, defaults to `true`

### Over/Under Prop

- `question`: Required, string
- `overPoints`: Required, float
- `underPoints`: Required, float
- `lineValue`: Optional, float (required for live stat tracking)
- `playerName`: Optional, string
- `playerId`: Optional, string (required for live stat tracking)
- `statType`: Optional, string (required for live stat tracking)
- `is_mandatory`: Optional, boolean, defaults to `false`

### Variable Option Prop

- `question`: Required, string
- `options`: Required, array of at least 2 options
  - `choice_text`: Required, string
  - `points`: Required, float
- `is_mandatory`: Optional, boolean, defaults to `false`

---

## Related Workflows

- [Edit Game](./game-edit.md) - Modifying game details
- [Delete Game](./game-delete.md) - Removing a game
- [Add Props to Game](./prop-add-to-game.md) - Adding props after creation
- [ESPN Integration](./live-stats-polling.md) - Live stat polling setup

---

*Last Updated: January 2026*

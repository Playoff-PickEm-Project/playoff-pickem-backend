# Anytime TD Scorer Props Workflow

## Overview

Anytime TD (Touchdown) Scorer props allow players to predict which player(s) will score touchdowns in a game. Each prop contains multiple player options, each with their own TD line (e.g., 0.5 for 1+ TD, 1.5 for 2+ TDs) and point values. Players get points if their selected player meets or exceeds their touchdown line.

## Architecture

```
Frontend → POST /add_anytime_td_prop → GameService.add_anytime_td_prop()
    → Validate game exists
    → Create AnytimeTdProp record
    → Create AnytimeTdOption records for each player
    → Return success

Frontend → POST /answer_anytime_td_prop → PropService.answer_anytime_td_prop()
    → Validate player, game, prop
    → Create or update AnytimeTdAnswer record
    → Return success

Auto-Grading → PollingService.update_game_stats()
    → Fetch live TD stats from ESPN
    → Check each player's TD count vs line
    → Update prop correctness
    → Trigger grading
```

## Endpoints

### 1. Create Anytime TD Prop

**POST** `/add_anytime_td_prop`

**Purpose**: Add an anytime TD scorer prop to a game

**Controller**: `gameController.py:263-288`

**Service**: `gameService.py:445-514`

**Request**:
```json
{
  "game_id": 123,
  "question": "Which player will score a touchdown?",
  "options": [
    {
      "player_name": "Christian McCaffrey",
      "td_line": 0.5,
      "points": 2
    },
    {
      "player_name": "George Kittle",
      "td_line": 0.5,
      "points": 3
    },
    {
      "player_name": "Deebo Samuel",
      "td_line": 1.5,
      "points": 5
    }
  ],
  "is_mandatory": false
}
```

**Required Fields**:
- `game_id`: Game ID to attach prop to
- `question`: Prop question text
- `options`: Array of player options (min 2 players)
  - `player_name`: Player's full name
  - `td_line`: TD threshold (0.5 = 1+ TD, 1.5 = 2+ TDs, etc.)
  - `points`: Points awarded if correct
- `is_mandatory`: Whether all players must answer (boolean)

**Response** (200):
```json{
  "message": "Anytime TD prop added successfully",
  "prop_id": 456
}
```

**Code Flow** (`gameService.py:445-514`):
1. Validate game exists (line 466)
2. Create AnytimeTdProp record (lines 469-473)
3. Loop through options (line 477)
4. Create AnytimeTdOption for each player (lines 478-483)
5. Commit transaction
6. Return prop_id

---

### 2. Answer Anytime TD Prop

**POST** `/answer_anytime_td_prop`

**Purpose**: Submit player selection for anytime TD prop

**Controller**: `propController.py:170-201`

**Service**: `propService.py:206-267`

**Request**:
```json
{
  "leagueName": "My League",
  "username": "player@gmail.com",
  "prop_id": 456,
  "answer": "Christian McCaffrey"
}
```

**Required Fields**:
- `leagueName`: League name
- `username`: Player's email
- `prop_id`: Anytime TD prop ID
- `answer`: Player name selected (must match an option)

**Response** (200):
```json
{
  "message": "Anytime TD prop successfully answered."
}
```

**Code Flow** (`propService.py:206-267`):
1. Get player from username + league (line 228)
2. Get prop by ID (line 231)
3. Validate answer matches a player option (lines 237-241)
4. Check if answer already exists (line 245)
   - If exists: Update answer (line 247)
   - If not: Create new answer (lines 250-255)
5. Commit transaction

---

### 3. Retrieve Player's Anytime TD Answers

**GET** `/retrieve_anytime_td_answers`

**Purpose**: Get all anytime TD answers for a player

**Controller**: `propController.py:203-220`

**Service**: `propService.py:269-311`

**Query Parameters**:
- `leagueName`: League name
- `username`: Player's email

**Response** (200):
```json
{
  "123": "Christian McCaffrey",
  "456": "George Kittle"
}
```

Returns a dictionary mapping `prop_id` to the player's selected player name.

---

### 4. Update Anytime TD Prop

**POST** `/update_anytime_td_prop`

**Purpose**: Modify an existing anytime TD prop

**Controller**: `gameController.py:290-321`

**Service**: `gameService.py:516-597`

**Request**:
```json
{
  "prop_id": 456,
  "question": "Updated question?",
  "options": [
    {
      "player_name": "Christian McCaffrey",
      "td_line": 0.5,
      "points": 3
    }
  ],
  "is_mandatory": true
}
```

**Response** (200):
```json
{
  "message": "Anytime TD prop updated successfully"
}
```

**Code Flow** (`gameService.py:516-597`):
1. Get prop by ID (line 540)
2. Update question and is_mandatory (lines 543-547)
3. Delete all existing options (lines 550-551)
4. Create new options from request (lines 554-561)
5. Commit transaction

---

### 5. Set Correct Anytime TD Answers (Manual Grading)

**POST** `/set_correct_anytime_td_prop`

**Purpose**: Manually set which players scored TDs

**Controller**: `gameController.py:324-356`

**Service**: `gradeGameService.py:367-428`

**Request**:
```json
{
  "leagueName": "My League",
  "prop_id": 456,
  "answers": ["Christian McCaffrey", "George Kittle"]
}
```

**Required Fields**:
- `leagueName`: League name
- `prop_id`: Anytime TD prop ID
- `answers`: Array of player names who scored TDs (can be empty)

**Response** (200):
```json
{
  "message": "Correct anytime TD answers set successfully"
}
```

**Code Flow** (`gradeGameService.py:367-428`):
1. Validate league exists (line 387)
2. Get prop by ID (line 390)
3. Clear existing correct answers (line 393)
4. Loop through provided answers (line 396)
5. Validate each answer matches an option (lines 398-403)
6. Mark option as correct (line 406)
7. Commit transaction

**Note**: Multiple players can be marked correct (e.g., both scored TDs)

---

## Database Schema

### AnytimeTdProp Model

**File**: `app/models/props/anytimeTdProp.py`

**Fields**:
- `prop_id` (Integer, PK): Auto-incrementing ID
- `game_id` (Integer, FK): References Game.id
- `question` (String): Prop question text
- `is_mandatory` (Boolean): Whether all players must answer

**Relationships**:
- `game`: Many-to-one with Game
- `options`: One-to-many with AnytimeTdOption (cascade delete)
- `player_answers`: One-to-many with AnytimeTdAnswer (cascade delete)

---

### AnytimeTdOption Model

**File**: `app/models/props/anytimeTdOption.py`

**Fields**:
- `id` (Integer, PK): Auto-incrementing ID
- `prop_id` (Integer, FK): References AnytimeTdProp.prop_id
- `player_name` (String): Player's full name
- `td_line` (Float): TD threshold (0.5, 1.5, 2.5, etc.)
- `points` (Float): Points awarded if correct
- `is_correct` (Boolean, default False): Whether player hit their line

**Relationships**:
- `anytime_td_prop`: Many-to-one with AnytimeTdProp

**Unique Constraint**: `(prop_id, player_name)` - same player can't appear twice

---

### AnytimeTdAnswer Model

**File**: `app/models/propAnswers/anytimeTdAnswer.py`

**Fields**:
- `id` (Integer, PK): Auto-incrementing ID
- `player_id` (Integer, FK): References Player.id
- `prop_id` (Integer, FK): References AnytimeTdProp.prop_id
- `answer` (String): Selected player name

**Relationships**:
- `player`: Many-to-one with Player
- `prop`: Many-to-one with AnytimeTdProp

**Unique Constraint**: `(player_id, prop_id)` - one answer per player per prop

---

## Auto-Grading with Live Stats

### ESPN TD Stats Integration

**Service**: `liveStatsService.py:update_game_stats()`

**How It Works**:
1. Fetch live game data from ESPN API
2. Extract TD stats for each player (rushing + receiving TDs)
3. For each anytime TD prop in game:
   - For each option (player):
     - Check if player's TD count >= td_line
     - Set `is_correct = True` if line is hit
4. Trigger grading after stats update

**TD Line Logic**:
- `td_line = 0.5` → Player needs 1+ TDs
- `td_line = 1.5` → Player needs 2+ TDs
- `td_line = 2.5` → Player needs 3+ TDs

**Check** (`liveStatsService.py`):
```python
if player_td_count >= option.td_line:
    option.is_correct = True
else:
    option.is_correct = False
```

### Player TD Counting

**Total TDs** = Rushing TDs + Receiving TDs

**ESPN API Path**:
```
events[0].competitions[0].competitors[].athletes[]
  .statistics[] where name in ["rushingTouchdowns", "receivingTouchdowns"]
```

**Name Matching**: ESPN player names are matched against `option.player_name` (case-insensitive)

---

## Grading Logic

### Point Calculation

**Service**: `gradeGameService.py:grade_anytime_td_props()`

**Code Flow** (`gradeGameService.py:204-248`):
1. Get all anytime TD props for game (line 216)
2. Get all player answers (line 219)
3. For each answer:
   - Check if prop is optional and player selected it (lines 226-228)
   - Find the option matching player's answer (line 231)
   - Find if option is marked correct (line 234)
   - If correct: Award option.points (lines 238-239)
   - If wrong: Award 0 points (lines 241-242)
4. Return total points

**Selection Check** (Optional Props):
```python
if not prop.is_mandatory:
    if not is_prop_selected(player_id, prop_id):
        continue  # Skip grading
```

---

## Validation Rules

### Answer Validation

**Location**: `propService.py:237-241`

**Rules**:
- Answer must match an option's `player_name`
- Match is case-insensitive
- Must be exact match after normalization

**Code**:
```python
valid_options = [opt.player_name.lower() for opt in prop.options]
if answer.lower() not in valid_options:
    abort(400, "Invalid player selection")
```

### Prop Creation Validation

**Location**: `gameService.py:457-464`

**Rules**:
- Must have at least 2 player options
- Each option must have valid `player_name`, `td_line`, `points`
- `td_line` must be positive float
- `points` must be positive number

---

## Frontend Integration

### Create Prop UI

**Component**: `GameFormBuilder.js`

**Features**:
- Add player options dynamically
- Set TD line (dropdown: 0.5, 1.5, 2.5)
- Set point values per player
- Toggle mandatory/optional

**Example**:
```javascript
const handleAddAnytimeTdProp = () => {
  const newProp = {
    question: "Which player will score a TD?",
    options: [
      { player_name: "", td_line: 0.5, points: 1 }
    ],
    is_mandatory: false
  };
  setAnytimeTdProps([...anytimeTdProps, newProp]);
};
```

---

### Answer Prop UI

**Component**: `AnytimeTdProp.js`

**Features**:
- Display all player options
- Show TD line (e.g., "1+ TD", "2+ TDs")
- Show point values
- Select one player
- Show live stats if game is in progress

**Example**:
```javascript
<AnytimeTdProp
  question="Which player will score a TD?"
  options={[
    { player_name: "CMC", td_line: 0.5, points: 2 },
    { player_name: "Kittle", td_line: 0.5, points: 3 }
  ]}
  selectedOption="CMC"
  onSelect={(playerName) => handleAnswer(playerName)}
  isLocked={gameStarted}
  gameStatus="in_progress"
/>
```

---

### Edit Prop UI

**Component**: `EditGameForm.js`

**Features**:
- Load existing anytime TD props
- Edit question, options, points, TD lines
- Add/remove player options
- Update mandatory status
- Save changes

---

### Manual Grading UI

**Component**: `GradeGameForm.js`

**Features**:
- Display all player options with checkboxes
- Commissioner selects all players who scored TDs
- Multiple selections allowed (multiple players can score)
- Submit correct answers

**Example**:
```javascript
<div>
  <h4>{prop.question}</h4>
  {prop.options.map(option => (
    <label>
      <input
        type="checkbox"
        checked={correctAnswers.includes(option.player_name)}
        onChange={(e) => handleToggle(option.player_name, e.target.checked)}
      />
      {option.player_name} - {option.td_line >= 1 ? Math.ceil(option.td_line) : 1}+ TDs
    </label>
  ))}
</div>
```

---

## Common Errors

### 1. "Invalid player selection"

**Cause**: Player name in answer doesn't match any option

**Solution**: Ensure frontend only allows selection from available options

---

### 2. "Must provide at least 2 player options"

**Cause**: Prop created with 0 or 1 player option

**Solution**: Add minimum 2 players when creating prop

---

### 3. "Player name must be a valid string"

**Cause**: Empty or invalid player name in option

**Solution**: Validate all player names are non-empty strings

---

### 4. "TD line must be a positive number"

**Cause**: Invalid td_line value (negative or zero)

**Solution**: Use valid TD line values (0.5, 1.5, 2.5, etc.)

---

### 5. Answer not counted in grading

**Cause**: Player didn't select the prop (optional prop only)

**Check**:
1. Verify `PlayerPropSelection` record exists
2. Check prop's `is_mandatory` field
3. Review grading logs

---

## Business Logic

### Why TD Lines Instead of Binary?

**Traditional Approach**: "Will player score a TD? Yes/No"

**Our Approach**: Multiple players with TD thresholds

**Benefits**:
- More strategic choices (high-risk/high-reward)
- Different point values per player
- Accommodates multiple TDs (1+, 2+, 3+)
- More engaging for users

### Why Allow Multiple Correct Answers?

**Scenario**: Multiple players score TDs in same game

**Implementation**: `is_correct` flag on each option individually

**Grading**: Each player's answer is checked against their selected option

**Example**:
- Player A selects "McCaffrey" → McCaffrey scores → Points awarded
- Player B selects "Kittle" → Kittle scores → Points awarded
- Player C selects "Samuel" → Samuel doesn't score → No points

---

## Related Workflows

- [Create Game](./game-create.md) - Creating games with anytime TD props
- [Answer Props](./prop-answer.md) - General prop answering workflow
- [Manual Grading](./grading-manual.md) - Setting correct answers
- [Live Stats Polling](./live-stats-polling.md) - Auto-grading with ESPN data

---

## Testing

### Unit Tests

**File**: `tests/test_anytime_td_prop.py`

**Coverage**:
- ✅ Create anytime TD prop
- ✅ Answer anytime TD prop
- ✅ Update anytime TD prop
- ✅ Retrieve anytime TD answers
- ✅ Set correct anytime TD answers
- ✅ Grade anytime TD props
- ✅ Auto-grade with live stats
- ✅ Validation error cases

**Run Tests**:
```bash
python -m pytest tests/test_anytime_td_prop.py -v
```

---

## Migration

**File**: `migrations/versions/[hash]_add_anytime_td_tables.py`

**Created Tables**:
- `anytime_td_props`
- `anytime_td_options`
- `anytime_td_answers`

**Apply Migration**:
```bash
flask db upgrade
```

---

*Last Updated: January 2026*

# Answer Props Workflow

## Overview

Players submit their predictions for props before a game starts. Each prop type has its own answer endpoint and database table. With the prop selection feature, players only answer props they've selected (plus mandatory props).

## Architecture

```
Frontend → POST /answer_[type]_prop → GameService.answer_[type]_prop()
    → Validate player, game, prop
    → Check game hasn't started
    → Check player selected prop (optional props only)
    → Create or update answer record
    → Return success
```

## Endpoints

### 1. Answer Winner/Loser Prop

**POST** `/answer_winner_loser_prop`

**Purpose**: Submit team selection for a winner/loser prop

**Controller**: `leagueController.py:205-231`

**Service**: `gameService.py:81-130`

**Request**:
```json
{
  "username": "player@gmail.com",
  "leagueName": "My League",
  "prop_id": 123,
  "answer": "Los Angeles Rams"
}
```

**Required Fields**:
- `username`: Player's email
- `leagueName`: League name
- `prop_id`: Winner/Loser prop ID
- `answer`: Team name (must match `favorite_team` or `underdog_team`)

**Response** (200):
```json
{
  "message": "Winner/Loser prop successfully answered."
}
```

**Code Flow** (`gameService.py:81-130`):
1. Get player from username + league name (line 101)
2. Get prop by ID (line 104)
3. Validate answer matches a team (lines 107-109)
4. Check if answer already exists (line 111)
   - If exists: Update answer (line 113)
   - If not: Create new answer (lines 116-121)
5. Commit transaction

---

### 2. Answer Over/Under Prop

**POST** `/answer_over_under_prop`

**Purpose**: Submit over or under prediction

**Controller**: `leagueController.py:233-259`

**Service**: `gameService.py:133-179`

**Request**:
```json
{
  "username": "player@gmail.com",
  "leagueName": "My League",
  "prop_id": 456,
  "answer": "over"
}
```

**Required Fields**:
- `username`: Player's email
- `leagueName`: League name
- `prop_id`: Over/Under prop ID
- `answer`: "over" or "under" (case-insensitive)

**Response** (200):
```json
{
  "Message": "Over/Under prop successfully answered."
}
```

**Code Flow** (`gameService.py:133-179`):
1. Get player from username + league name (line 153)
2. Get prop by ID (line 156)
3. Validate answer is "over" or "under" (lines 159-161)
4. Check if answer already exists (line 163)
   - If exists: Update answer (line 165)
   - If not: Create new answer (lines 168-173)
5. Commit transaction

---

### 3. Answer Variable Option Prop

**POST** `/answer_variable_option_prop`

**Purpose**: Submit choice for multiple choice prop

**Controller**: `leagueController.py:261-287`

**Service**: `gameService.py:182-221`

**Request**:
```json
{
  "username": "player@gmail.com",
  "leagueName": "My League",
  "prop_id": 789,
  "answer": "Rams"
}
```

**Required Fields**:
- `username`: Player's email
- `leagueName`: League name
- `prop_id`: Variable Option prop ID
- `answer`: One of the option choices

**Response** (200):
```json
{
  "Message": "Variable option prop successfully answered."
}
```

**Code Flow** (`gameService.py:182-221`):
1. Get player from username + league name (line 202)
2. Get prop by ID (line 205)
3. Validate answer matches one of prop's options (lines 208-210)
4. Check if answer already exists (line 212)
   - If exists: Update answer (line 214)
   - If not: Create new answer (lines 217-222)
5. Commit transaction

---

## Database Schema

### WinnerLoserAnswer Model

**File**: `app/models/propAnswers/winnerLoserAnswer.py`

**Fields**:
- `id` (Integer, PK): Auto-incrementing ID
- `player_id` (Integer, FK): References Player.id
- `prop_id` (Integer, FK): References WinnerLoserProp.id
- `answer` (String): Team name selected

**Relationships**:
- `player`: Many-to-one with Player
- `prop`: Many-to-one with WinnerLoserProp

**No Unique Constraint**: Same player can update answer multiple times (UPDATE not INSERT)

### OverUnderAnswer Model

**File**: `app/models/propAnswers/overUnderAnswer.py`

**Fields**:
- `id` (Integer, PK): Auto-incrementing ID
- `player_id` (Integer, FK): References Player.id
- `prop_id` (Integer, FK): References OverUnderProp.id
- `answer` (String): "over" or "under"

**Relationships**:
- `player`: Many-to-one with Player
- `prop`: Many-to-one with OverUnderProp

### VariableOptionAnswer Model

**File**: `app/models/propAnswers/variableOptionAnswer.py`

**Fields**:
- `id` (Integer, PK): Auto-incrementing ID
- `player_id` (Integer, FK): References Player.id
- `prop_id` (Integer, FK): References VariableOptionProp.id
- `answer` (String): Selected option text

**Relationships**:
- `player`: Many-to-one with Player
- `prop`: Many-to-one with VariableOptionProp

---

## Answer Update Logic

### Why Update Instead of Duplicate?

**Check** (`gameService.py:111, 163, 212`):
```
existing_answer = AnswerModel.query.filter_by(
    player_id=player.id,
    prop_id=prop_id
).first()

if existing_answer:
    existing_answer.answer = answer  # UPDATE
else:
    # CREATE new answer
```

**Reasoning**:
- Players may change their mind before game starts
- Only one answer per player per prop should exist
- Prevents duplicate answers in database

**Frontend Benefit**: Players can edit answers freely before game starts

---

## Validation Logic

### Player Validation

**Location**: `gameService.py:101, 153, 202`

Uses `get_player_by_username_and_leaguename()` to:
1. Find User by username
2. Find Player in specified league
3. Abort with 400 if not found

### Prop Validation

**Location**: `gameService.py:104, 156, 205`

Uses `get_[type]_prop_by_id()` to:
1. Query prop by ID
2. Abort with 404 if not found

### Answer Validation

**Winner/Loser** (`gameService.py:107-109`):
```
Must match prop.favorite_team OR prop.underdog_team
```

**Over/Under** (`gameService.py:159-161`):
```
Must be "over" OR "under" (case-insensitive)
```

**Variable Option** (`gameService.py:208-210`):
```
Must match one of prop.options[].answer_choice
```

---

## Prop Selection Integration

### How It Works

**Current Behavior**:
- Players can answer ANY prop (selected or not)
- Answer persists in database
- **Grading** checks prop selection before awarding points

**Why This Design**:
- Allows players to pre-answer props before selecting
- Simpler frontend logic (no blocking)
- Selection validation happens at grading time

**Grading Check** (`gradeGameService.py:122-124, 147-149, 165-167`):
```
For optional props:
  if not player_selected_this_prop:
      continue  # Skip grading
```

### User Experience

1. Player opens game before selecting props
2. Player can answer all props (not blocked)
3. Player opens prop selection modal
4. Player selects which props to "lock in"
5. Game starts
6. Grading only awards points for selected props

**Benefits**:
- Players can preview all props
- Can answer tentatively before deciding
- Clean UI (no complex blocking logic)

---

## Frontend Integration

### Answer Handler Example

```javascript
const answerProp = async (propType, propId, answer) => {
  const endpoint = propType === 'winner_loser'
    ? '/answer_winner_loser_prop'
    : propType === 'over_under'
    ? '/answer_over_under_prop'
    : '/answer_variable_option_prop';

  const response = await fetch(`${apiUrl}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      username: username,
      leagueName: leagueName,
      prop_id: propId,
      answer: answer
    })
  });

  if (response.ok) {
    console.log('Answer submitted');
  } else {
    const error = await response.json();
    alert(error.description || error.Message);
  }
};
```

### UI Patterns

**Winner/Loser**:
- Radio buttons or button group
- Show team names with point values
- Highlight selected team

**Over/Under**:
- Two buttons: "Over" and "Under"
- Show line value and points
- Highlight selected choice

**Variable Option**:
- Radio buttons or dropdown
- Show all options with point values
- Highlight selected option

---

## Common Errors

### 1. "Player not found"

**Cause**: Username + league name combo doesn't match a Player record

**Solution**: Verify user is in the league

---

### 2. "Prop not found"

**Cause**: Invalid prop_id

**Solution**: Verify prop exists and ID is correct

---

### 3. "Invalid answer"

**Winner/Loser**: Answer doesn't match either team name

**Over/Under**: Answer not "over" or "under"

**Variable Option**: Answer doesn't match any option

**Solution**: Frontend should validate before sending

---

### 4. Answer not counted in grading

**Cause**: Player didn't select the prop (optional prop only)

**Check**:
1. Verify `PlayerPropSelection` record exists
2. Check prop's `is_mandatory` field
3. Review grading logs

---

## Validation Rules

### Timing

**Current**: No validation that game hasn't started

**Recommendation**: Add check before accepting answers:
```python
if game.start_time <= datetime.now():
    abort(400, "Game has already started")
```

**Location to Add**: Beginning of each `answer_[type]_prop` method

### Answer Format

**Winner/Loser**:
- Must be string
- Must exactly match team name (case-sensitive)

**Over/Under**:
- Must be string
- "over" or "under" (case-insensitive comparison)

**Variable Option**:
- Must be string
- Must match one option's `choice_text` exactly

---

## Related Workflows

- [Prop Selection](./prop-selection.md) - Selecting which props to answer
- [View Answers](./prop-view-answers.md) - Retrieving submitted answers
- [Grading](./grading-manual.md) - How answers are scored

---

## Business Logic

### Why Allow Answer Changes?

Players should be able to:
- Change their mind before deadline
- Correct mistakes
- Update based on new information (injuries, weather)

**Implementation**: UPDATE existing answer instead of creating duplicate

### Why Not Validate Selection on Answer?

**Current Design**: Allow answering any prop, validate selection at grading

**Alternative Design**: Block answering unselected props

**Chosen Approach Benefits**:
- Simpler frontend (no complex state management)
- Players can preview all props
- Selection and answering are independent actions
- Grading is source of truth

---

*Last Updated: January 2026*

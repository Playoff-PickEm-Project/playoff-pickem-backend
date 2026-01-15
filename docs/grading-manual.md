# Manual Grading Workflow

## Overview

Manual grading allows the League Manager to set correct answers for props and trigger the grading process. The system then calculates points for all players based on their answers and updates the leaderboard.

## Architecture

```
League Manager → POST /set_correct_answer → GradeGameService.set_correct_[type]_prop()
    → If game already graded: Deduct old points (regrading)
    → Update correct_answer field
    → Commit changes

League Manager → POST /grade_game → GradeGameService.grade_game()
    → Iterate through all props
    → For each prop, get all player answers
    → Check if answer matches correct_answer
    → Award points based on prop type
    → Mark game as graded
```

## Endpoints

### 1. Set Winner/Loser Correct Answer

**POST** `/set_correct_winner_loser_prop`

**Purpose**: Set which team won the game

**Controller**: `gameController.py:56-79`

**Service**: `gradeGameService.py:206-261`

**Request**:
```json
{
  "leagueName": "My League",
  "prop_id": 123,
  "correctAnswer": "Los Angeles Rams"
}
```

**Response** (200):
```json
{
  "message": "Correct answer set successfully."
}
```

**Code Flow**:
1. Validate league name, prop ID, and answer (validators at lines 225-227)
2. Get prop from database (`get_winner_loser_prop_by_id` at line 229)
3. Get associated game (line 232)
4. **If game already graded** (line 236):
   - Get all answers for this prop
   - Find players who answered the OLD correct answer
   - Deduct their old points (lines 248-253)
5. Update prop's `correct_answer` field (line 257)
6. Commit to database

**Regrading Logic**: If commissioner changes the correct answer after grading, the system automatically deducts points from players who had the old answer correct.

---

### 2. Set Over/Under Correct Answer

**POST** `/set_correct_over_under_prop`

**Purpose**: Set whether the result was "over" or "under"

**Controller**: `gameController.py:81-104`

**Service**: `gradeGameService.py:263-318`

**Request**:
```json
{
  "leagueName": "My League",
  "prop_id": 456,
  "correctAnswer": "over"
}
```

**Valid Answers**: "over" or "under" (case-insensitive)

**Response** (200):
```json
{
  "message": "Correct answer set successfully."
}
```

**Code Flow**: Same as Winner/Loser (validation → check if graded → deduct old points → update)

**Case Insensitive**: Comparisons use `.lower()` at line 305

---

### 3. Set Variable Option Correct Answer

**POST** `/set_correct_variable_option_prop`

**Purpose**: Set correct answer(s) for multiple choice props

**Controller**: `gameController.py:106-129`

**Service**: `gradeGameService.py:149-204`

**Request**:
```json
{
  "leagueName": "My League",
  "prop_id": 789,
  "correctAnswer": ["Rams", "Neither"]
}
```

**Note**: `correctAnswer` is an **array** (can have multiple correct answers)

**Response** (200):
```json
{
  "message": "Correct answer set successfully."
}
```

**Code Flow**: Same regrading logic, but handles array of correct answers (line 183)

---

### 4. Grade Game

**POST** `/grade_game`

**Purpose**: Calculate and award points to all players for a game

**Controller**: `gameController.py:131-153`

**Service**: `gradeGameService.py:90-182`

**Request**:
```json
{
  "game_id": 123
}
```

**Response** (200):
```json
{
  "message": "Game graded successfully."
}
```

**Code Flow**:

1. **Validate** game exists (lines 108-110)

2. **Grade Winner/Loser Props** (lines 112-137):
   - For each prop, get all player answers
   - For optional props: Check if player selected this prop (lines 122-124)
   - If answer matches `correct_answer` and is favorite: Add `favorite_points`
   - If answer matches `correct_answer` and is underdog: Add `underdog_points`

3. **Grade Over/Under Props** (lines 139-156):
   - For each prop, get all player answers
   - For optional props: Check if player selected this prop (lines 147-149)
   - Case-insensitive comparison (line 152)
   - Award `over_points` or `under_points` based on answer

4. **Grade Variable Option Props** (lines 158-178):
   - For each prop, get all player answers
   - For optional props: Check if player selected this prop (lines 165-167)
   - Loop through correct answers array
   - Find matching option and award its points

5. **Mark game as graded** (line 180): Set `game.graded = 1`

6. **Commit all point changes** (line 182)

**IMPORTANT**: Grading only awards points for props that players have:
- Answered AND
- Selected (for optional props)

---

## Database Schema

### Correct Answer Fields

**Winner/Loser Prop**:
- `correct_answer` (String, nullable): Team name that won (e.g., "Los Angeles Rams")
- `team_a_score` (Integer, nullable): Team A final score (used for auto-grading)
- `team_b_score` (Integer, nullable): Team B final score (used for auto-grading)

**Over/Under Prop**:
- `correct_answer` (String, nullable): "over" or "under"
- `current_value` (Float, nullable): Actual stat value (used for auto-grading)

**Variable Option Prop**:
- `correct_answer` (ARRAY of Strings, nullable): List of correct choices

### Game Grading State

**File**: `app/models/gameModel.py`

```
graded (Integer, default=0):
  - 0: Not graded yet
  - 1: Graded
```

**Purpose**: Tracks if game has been graded to enable regrading logic

---

## Regrading Logic

### What is Regrading?

When a commissioner changes a correct answer **after** the game has been graded, the system:
1. Finds all players who answered the OLD correct answer
2. Deducts their points
3. Updates to the NEW correct answer
4. Next grading will award points based on new answer

### Example Scenario

**Initial State**:
- Prop: "Who will win?"
- Correct answer set to: "Rams"
- Game graded
- Player A picked "Rams" → got 1 point
- Player B picked "Panthers" → got 0 points

**Commissioner Changes Mind**:
- Commissioner sets correct answer to: "Panthers"
- System detects `game.graded = 1` (line 236 in gradeGameService.py)
- Finds Player A answered "Rams" (the OLD correct answer)
- Deducts 1 point from Player A (lines 248-253)
- Updates `correct_answer` to "Panthers"

**Next Grading** (if commissioner clicks "Grade Game" again):
- Player A has 0 points (deducted)
- Player B would get points for "Panthers"

### Code Reference

**Regrading Check**: `gradeGameService.py:236`
```
if game.graded != 0:
    # Deduct points for old correct answer
```

**Deduction Logic**:
- Winner/Loser: Lines 245-253
- Over/Under: Lines 305-311
- Variable Option: Lines 189-198

---

## Frontend Integration

### Setting Correct Answer

**Component**: `GradeGameForm.js`

**Example**:
```javascript
const setCorrectAnswer = async (propType, propId, correctAnswer) => {
  const endpoint = propType === 'winner_loser'
    ? '/set_correct_winner_loser_prop'
    : propType === 'over_under'
    ? '/set_correct_over_under_prop'
    : '/set_correct_variable_option_prop';

  const response = await fetch(`${apiUrl}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      leagueName: leagueName,
      prop_id: propId,
      correctAnswer: correctAnswer
    })
  });

  if (response.ok) {
    console.log('Correct answer set');
  }
};
```

### Grading Game

```javascript
const gradeGame = async (gameId) => {
  const response = await fetch(`${apiUrl}/grade_game`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ game_id: gameId })
  });

  if (response.ok) {
    console.log('Game graded successfully');
    // Refresh standings/leaderboard
  }
};
```

---

## Workflow Steps

### For League Manager

1. **Wait for Game to Complete**: Game must be finished
2. **Set Correct Answers**:
   - For each Winner/Loser prop: Choose winning team
   - For each Over/Under prop: Choose "over" or "under"
   - For each Variable Option prop: Choose correct option(s)
3. **Grade Game**: Click "Grade Game" button
4. **View Results**: Check updated leaderboard
5. **Regrade if Needed**: Can change answers and regrade

### System Processing

1. **Before Grading**:
   - All props must have `correct_answer` set
   - Game must have at least one player answer

2. **During Grading**:
   - Iterate through all props in game
   - Get all player answers for each prop
   - Check prop selection (for optional props)
   - Compare answer to `correct_answer`
   - Award points if match

3. **After Grading**:
   - `game.graded` set to 1
   - All player points updated in database
   - Leaderboard reflects new standings

---

## Point Award Logic

### Winner/Loser Props

**Location**: `gradeGameService.py:127-137`

```
If player answered correctly:
  - If answer == favorite_team: player.points += favorite_points
  - If answer == underdog_team: player.points += underdog_points
```

**Example**:
- Favorite: "Rams" (1 point)
- Underdog: "Panthers" (2 points)
- Correct answer: "Rams"
- Player picked "Rams" → gets 1 point
- Player picked "Panthers" → gets 0 points

### Over/Under Props

**Location**: `gradeGameService.py:152-156`

```
If player answered correctly (case-insensitive):
  - If answer == "over": player.points += over_points
  - If answer == "under": player.points += under_points
```

**Example**:
- Over: 1.5 points
- Under: 1.5 points
- Correct answer: "over"
- Player picked "over" → gets 1.5 points
- Player picked "under" → gets 0 points

### Variable Option Props

**Location**: `gradeGameService.py:169-178`

```
For each correct answer in correct_answer array:
  If player's answer matches:
    Find corresponding option
    player.points += option.answer_points
```

**Example**:
- Options: ["Rams" (1pt), "Panthers" (2pts), "Neither" (3pts)]
- Correct answers: ["Rams", "Neither"]
- Player picked "Rams" → gets 1 point
- Player picked "Neither" → gets 3 points
- Player picked "Panthers" → gets 0 points

---

## Common Errors

### 1. "Prop not found"

**Cause**: Invalid `prop_id`

**Solution**: Verify prop exists and ID is correct

---

### 2. "Game not found"

**Cause**: Prop's `game_id` doesn't match existing game

**Solution**: Check database integrity

---

### 3. No points awarded after grading

**Possible Causes**:
- Correct answers not set before grading
- No player answers submitted
- Players didn't select the prop (for optional props)
- Answers don't match correct answer format

**Debug**:
- Check `correct_answer` field is populated
- Verify player answers exist in database
- Check `PlayerPropSelection` records for optional props

---

### 4. Points not deducted during regrade

**Cause**: Game wasn't marked as graded (`game.graded = 0`)

**Solution**: Ensure grading was completed (check `game.graded = 1`)

---

## Validation Rules

### Correct Answer Format

**Winner/Loser**:
- Must be a string
- Should match `favorite_team` or `underdog_team` exactly

**Over/Under**:
- Must be "over" or "under" (case-insensitive)

**Variable Option**:
- Must be an array of strings
- Each string should match an option's `choice_text`

### Game State

- Game cannot be deleted if graded (prevents data loss)
- Players cannot answer props after game is graded
- Correct answers can be changed after grading (triggers regrade)

---

## Related Workflows

- [Auto-Grading](./grading-auto.md) - Automatic grading from live stats
- [Grading with Prop Selection](./grading-prop-selection.md) - How selections affect grading
- [View Standings](./standings.md) - Viewing updated leaderboard

---

*Last Updated: January 2026*

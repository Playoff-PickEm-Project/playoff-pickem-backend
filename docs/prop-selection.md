# Prop Selection Workflow

## Overview

The Prop Selection feature allows players to choose which optional props they want to answer from a pool, rather than answering all props. League Managers can designate props as "mandatory" (all players must answer) or "optional" (players choose from a pool), and set a `prop_limit` to control how many optional props players must select.

## Architecture

```
Frontend Modal → POST /select_prop → PropService.select_prop_for_player()
    → Validate player, game, prop
    → Check if prop is mandatory (reject if yes)
    → Check selection count vs prop_limit
    → Create PlayerPropSelection record
    → Return success

Frontend Modal → DELETE /deselect_prop/{id} → Delete PlayerPropSelection
    → Return success
```

## Key Concepts

### Mandatory vs Optional Props

- **Mandatory Props**: Props that ALL players must answer (e.g., "Who will win?")
  - Cannot be deselected
  - Not counted toward `prop_limit`
  - Shown with lock icon in UI
  - Default for Winner/Loser props

- **Optional Props**: Props that players can choose to answer
  - Players select up to `prop_limit` props from the pool
  - Counted toward `prop_limit`
  - Can be selected/deselected before game starts
  - Default for Over/Under and Variable Option props

### Prop Limit

The `prop_limit` field on the Game model determines how many optional props each player must select:

```
Total props player answers = (Mandatory props) + (prop_limit optional props)
```

**Example**:
- Game has 1 mandatory Winner/Loser prop + 4 optional Over/Under props
- `prop_limit = 2`
- Player must answer: 1 mandatory + 2 optional (player's choice) = 3 total props

---

## Endpoints

### 1. Select Prop

**Endpoint**: `POST /select_prop`

**Purpose**: Add a prop to a player's selected props for a game

**Controller**: `propController.py:283-316`

**Service**: `propService.py:12-81` (`PropService.select_prop_for_player`)

**Authentication**: Required (session)

#### Request Format

```json
{
  "player_id": 123,
  "game_id": 456,
  "prop_type": "over_under",
  "prop_id": 789
}
```

**Required Fields**:
- `player_id` (integer): Player's ID
- `game_id` (integer): Game's ID
- `prop_type` (string): "winner_loser", "over_under", or "variable_option"
- `prop_id` (integer): The prop's ID

#### Response Format

**Success** (201):
```json
{
  "message": "Prop selected successfully",
  "selection": {
    "id": 1,
    "player_id": 123,
    "game_id": 456,
    "prop_type": "over_under",
    "prop_id": 789
  }
}
```

**Error** (400):
```json
{
  "description": "Error message here"
}
```

**Possible Errors**:
- "Player not found"
- "Game not found"
- "Prop not found"
- "This prop does not belong to the specified game"
- "You have already selected this prop"
- "Mandatory props cannot be manually selected"
- "You have already selected the maximum number of props (2/2)"

#### Code Reference

**Controller** (`propController.py:283-316`):
```python
@propController.route("/select_prop", methods=['POST'])
def select_prop():
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        game_id = data.get('game_id')
        prop_type = data.get('prop_type')
        prop_id = data.get('prop_id')

        selection = PropService.select_prop_for_player(player_id, game_id, prop_type, prop_id)

        return jsonify({
            "message": "Prop selected successfully",
            "selection": selection.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"description": str(e)}), 400
```

**Service** (`propService.py:12-81`):
```python
@staticmethod
def select_prop_for_player(player_id, game_id, prop_type, prop_id):
    # 1. Validate player exists
    player = get_player_by_id(player_id)
    if not player:
        abort(400, description="Player not found")

    # 2. Validate game exists
    game = get_game_by_id(game_id)
    if not game:
        abort(400, description="Game not found")

    # 3. Get the prop based on type
    prop = PropService._get_prop_by_type(prop_type, prop_id)
    if not prop:
        abort(400, description=f"Prop not found")

    # 4. Ensure prop belongs to this game
    if int(prop.game_id) != int(game_id):
        abort(400, description=f"This prop does not belong to the specified game.")

    # 5. Check if already selected
    if check_prop_already_selected(player_id, game_id, prop_type, prop_id):
        abort(400, description="You have already selected this prop")

    # 6. Check if prop is mandatory
    if PropService._is_prop_mandatory(prop):
        abort(400, description="Mandatory props cannot be manually selected")

    # 7. Check prop limit
    current_count = get_player_prop_selection_count(player_id, game_id)
    if current_count >= game.prop_limit:
        abort(400, description=f"You have already selected the maximum number of props ({current_count}/{game.prop_limit})")

    # 8. Create selection
    selection = create_player_prop_selection(player_id, game_id, prop_type, prop_id)

    return selection
```

---

### 2. Deselect Prop

**Endpoint**: `DELETE /deselect_prop/<int:selection_id>`

**Purpose**: Remove a prop from a player's selected props

**Controller**: `propController.py:318-340`

**Repository**: `propRepository.py:241-256` (`delete_player_prop_selection`)

**Authentication**: Required (session)

#### Request Format

```http
DELETE /deselect_prop/123 HTTP/1.1
Content-Type: application/json

{
  "player_id": 456
}
```

**URL Parameter**:
- `selection_id` (integer): ID of the PlayerPropSelection record

**Body**:
- `player_id` (integer): Player's ID (for authorization)

#### Response Format

**Success** (200):
```json
{
  "message": "Prop deselected successfully"
}
```

**Error** (400/404):
```json
{
  "description": "Selection not found"
}
```

#### Code Reference

**Controller** (`propController.py:318-340`):
```python
@propController.route("/deselect_prop/<int:selection_id>", methods=['DELETE'])
def deselect_prop(selection_id):
    try:
        data = request.get_json()
        player_id = data.get('player_id')

        success = delete_player_prop_selection(selection_id, player_id)

        if success:
            return jsonify({"message": "Prop deselected successfully"}), 200
        else:
            return jsonify({"description": "Selection not found"}), 404
    except Exception as e:
        return jsonify({"description": str(e)}), 400
```

---

### 3. Get Player Selected Props

**Endpoint**: `GET /get_player_selected_props`

**Purpose**: Retrieve all props a player has selected for a game

**Controller**: `propController.py:342-368`

**Repository**: `propRepository.py:195-207` (`get_player_prop_selections_for_game`)

**Authentication**: Required (session)

#### Request Format

```http
GET /get_player_selected_props?player_id=123&game_id=456 HTTP/1.1
```

**Query Parameters**:
- `player_id` (integer): Player's ID
- `game_id` (integer): Game's ID

#### Response Format

**Success** (200):
```json
{
  "selections": [
    {
      "id": 1,
      "player_id": 123,
      "game_id": 456,
      "prop_type": "over_under",
      "prop_id": 789
    },
    {
      "id": 2,
      "player_id": 123,
      "game_id": 456,
      "prop_type": "over_under",
      "prop_id": 790
    }
  ]
}
```

#### Code Reference

```python
@propController.route("/get_player_selected_props", methods=['GET'])
def get_player_selected_props():
    try:
        player_id = request.args.get('player_id')
        game_id = request.args.get('game_id')

        selections = get_player_prop_selections_for_game(int(player_id), int(game_id))

        return jsonify({
            "selections": [s.to_dict() for s in selections]
        }), 200
    except Exception as e:
        return jsonify({"description": str(e)}), 400
```

---

### 4. Reset Player Selections

**Endpoint**: `POST /reset_player_selections`

**Purpose**: Clear all prop selections for a player in a game

**Controller**: `propController.py:370-389`

**Repository**: `propRepository.py:258-271` (`delete_all_player_selections_for_game`)

**Authentication**: Required (session)

#### Request Format

```json
{
  "player_id": 123,
  "game_id": 456
}
```

#### Response Format

**Success** (200):
```json
{
  "message": "All prop selections reset successfully"
}
```

---

## Database Schema

### PlayerPropSelection Model

**File**: `app/models/playerPropSelection.py`

```python
class PlayerPropSelection(db.Model):
    __tablename__ = 'player_prop_selection'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    prop_type = db.Column(db.String(50), nullable=False)  # 'winner_loser', 'over_under', 'variable_option'
    prop_id = db.Column(db.Integer, nullable=False)  # ID of the actual prop

    # Relationships
    player = db.relationship('Player', back_populates='prop_selections')
    game = db.relationship('Game', back_populates='prop_selections')

    # Unique constraint: player can only select each prop once
    __table_args__ = (
        db.UniqueConstraint('player_id', 'game_id', 'prop_type', 'prop_id',
                          name='unique_player_prop_selection'),
    )
```

**Fields**:
- `id` (Integer, PK): Auto-incrementing ID
- `player_id` (Integer, FK): References `player.id`
- `game_id` (Integer, FK): References `game.id`
- `prop_type` (String): Type of prop ("winner_loser", "over_under", "variable_option")
- `prop_id` (Integer): ID of the actual prop (not a foreign key, polymorphic)

**Unique Constraint**: Prevents duplicate selections of the same prop

---

## Frontend Integration

### Prop Selection Modal

**Component**: `PropSelectionModal.js`

**Trigger**: Shown when player clicks on an upcoming game

**Features**:
- Separates mandatory props (locked, always shown at top)
- Shows optional props with selection checkboxes
- Displays selection count: "Selected 2/2 optional props"
- Submit button disabled until correct number selected
- Real-time validation

**Example Usage**:
```javascript
<PropSelectionModal
  show={showPropSelectionModal}
  onClose={() => setShowPropSelectionModal(false)}
  mandatoryProps={mandatoryProps}
  optionalProps={optionalProps}
  selectedPropIds={selectedPropIds}
  propLimit={propLimit}
  onSelectProp={handleSelectProp}
  onDeselectProp={handleDeselectProp}
  hasCompletedSelection={hasCompletedSelection}
/>
```

### Select Prop Handler

**File**: `GamePage.js:402-436`

```javascript
const handleSelectProp = async (propType, propId) => {
  if (isLocked) return

  try {
    const res = await fetch(`${apiUrl}/select_prop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        player_id: playerId,
        game_id: gameId,
        prop_type: propType,
        prop_id: propId,
      }),
    })

    if (!res.ok) {
      let errorMsg = 'Failed to select prop';
      try {
        const error = await res.json();
        errorMsg = error.description || error.message || errorMsg;
      } catch {
        errorMsg = res.statusText || errorMsg;
      }
      throw new Error(errorMsg);
    }

    const data = await res.json()
    setSelectedPropIds((prev) => [...prev, data.selection])
  } catch (e) {
    console.error('Select prop error:', e);
    alert(e.message || 'Failed to select prop')
  }
}
```

---

## Grading Integration

### How Selection Affects Grading

**File**: `gradeGameService.py:112-178`

When grading a game, the system checks if a player has selected each optional prop:

```python
# For each prop in the game
for prop in game.over_under_props:
    answers = get_over_under_answers_for_prop(prop.id)

    for answer in answers:
        player = get_player_by_id(answer.player_id)

        # For optional props, check if player selected this prop
        if not prop.is_mandatory:
            if not GradeGameService._has_player_selected_prop(
                player.id, game.id, "over_under", prop.id
            ):
                continue  # Skip grading if player didn't select this prop

        # Award points if answer is correct
        if player is not None and answer.answer.lower() == prop.correct_answer.lower():
            if answer.answer.lower() == "over":
                player.points += prop.over_points
            elif answer.answer.lower() == "under":
                player.points += prop.under_points
```

**Key Points**:
1. **Mandatory props**: Always graded (no selection check)
2. **Optional props**: Only graded if `PlayerPropSelection` exists
3. **Deselected props**: Even if answered, won't be graded if not currently selected

---

## User Flow

### Player Perspective

1. **View Games**: Player navigates to league home
2. **Click Upcoming Game**: Modal opens showing props
3. **See Mandatory Props**: Shown at top with lock icon (always required)
4. **See Optional Props**: Shown below with checkboxes
5. **Select Props**: Click to select up to `prop_limit` optional props
6. **Submit**: Click "Confirm Selection" when limit reached
7. **Answer Props**: Modal closes, player can now answer selected props
8. **Change Selection**: Can reopen modal and change selections until game starts
9. **Game Starts**: Selections locked, player answers their selected props
10. **Grading**: Only selected props are graded

### League Manager Perspective

1. **Create Game**: Set `prop_limit` (e.g., 2)
2. **Add Props**: Mark each prop as mandatory or optional
   - Winner/Loser defaults to mandatory
   - Over/Under defaults to optional
   - Variable Option defaults to optional
3. **Players Select**: Players choose their optional props
4. **Game Completes**: Grade game (only selected props are graded)

---

## Common Errors

### 1. "Mandatory props cannot be manually selected"

**Cause**: Frontend tried to call `/select_prop` for a mandatory prop

**Solution**: Mandatory props should be auto-selected and shown locked in UI

**Prevention**: Check `is_mandatory` before allowing selection

---

### 2. "You have already selected the maximum number of props"

**Cause**: Player trying to select more props than `prop_limit` allows

**Solution**: Deselect a prop before selecting a new one

**Prevention**: Disable select buttons when limit reached

---

### 3. "This prop does not belong to the specified game"

**Cause**: `prop_id` doesn't match `game_id`

**Solution**: Verify prop belongs to correct game

**Prevention**: Only show props for current game in modal

---

### 4. Player gets points for deselected prop

**Cause**: Grading logic not checking selections (this was a bug, now fixed)

**Solution**: Ensure grading checks `_has_player_selected_prop()` for optional props

**Fixed In**: `gradeGameService.py:122-124, 147-149, 165-167`

---

## Testing

### Test Coverage

**File**: `tests/test_prop_selection_grading.py`

**Test Cases**:
1. `test_multiple_players_different_selections` - Multiple players select different props
2. `test_player_only_graded_on_selected_props` - Player only gets points for selected props
3. `test_all_players_answer_mandatory_props` - Mandatory props always required
4. `test_no_points_for_unselected_props` - No points for unselected props
5. `test_deselected_prop_not_graded` - Deselected props don't count toward score

**Run Tests**:
```bash
python -m pytest tests/test_prop_selection_grading.py -v
```

---

## Related Workflows

- [Create Game](./game-create.md) - Setting prop_limit and is_mandatory
- [Grading with Prop Selection](./grading-prop-selection.md) - How grading considers selections
- [Answer Props](./prop-answer.md) - Players answer selected props

---

*Last Updated: January 2026*

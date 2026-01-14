# Create League Workflow

## Overview

Creating a league establishes a new competition group where users can join as players and compete by answering props for games. The creator automatically becomes the League Manager (commissioner).

## Architecture

```
Frontend Form → POST /create_league → LeagueService.create_league()
    → Create League record
    → Generate unique join code
    → Create Player record for creator
    → Set creator as commissioner
    → Return league details + join code
```

## Endpoint

**POST** `/create_league`

**Controller**: `leagueController.py:16-38`

**Service**: `leagueService.py:16-61`

**Authentication**: Required (session)

---

## Request Format

```json
{
  "leagueName": "NFL Playoff Challenge 2026",
  "username": "user@gmail.com"
}
```

**Required Fields**:
- `leagueName` (string): Unique name for the league
- `username` (string): Email of the user creating the league (from session)

**Validation**:
- League name must be unique across all leagues
- Username must match authenticated session user
- League name cannot be empty

---

## Response Format

### Success (200)

```json
{
  "message": "League created successfully.",
  "league": {
    "id": 123,
    "league_name": "NFL Playoff Challenge 2026",
    "join_code": "ABC123XYZ",
    "commissioner_id": 456,
    "commissioner": {
      "id": 456,
      "name": "user@gmail.com",
      "league_id": 123,
      "points": 0
    },
    "league_players": [
      {
        "id": 456,
        "name": "user@gmail.com",
        "league_id": 123,
        "points": 0
      }
    ]
  }
}
```

**Key Fields Returned**:
- `join_code`: Unique 9-character code for others to join
- `commissioner_id`: ID of the creator's Player record
- `league_players`: Array with creator as first player

### Error Responses

**400 - Validation Error**:
```json
{
  "description": "League name already exists"
}
```

**400 - Empty League Name**:
```json
{
  "description": "League name cannot be empty"
}
```

**404 - User Not Found**:
```json
{
  "description": "User does not exist"
}
```

---

## Code Flow

### 1. Controller Layer

**File**: `app/controllers/leagueController.py:16-38`

**Lines 16-38**: Extract `leagueName` and `username` from request body, call service, return response

### 2. Service Layer

**File**: `app/services/leagueService.py:16-61`

**Step-by-step**:

1. **Validate League Name** (line 38):
   - Check not empty
   - Check uniqueness using `get_league_by_name()`
   - Abort with 400 if exists

2. **Get User** (line 44):
   - Query User model by username
   - Abort with 404 if not found

3. **Generate Join Code** (lines 47-52):
   - Create random 9-character alphanumeric code
   - Check uniqueness in database
   - Regenerate if duplicate (lines 50-52)

4. **Create League** (lines 54-57):
   - Initialize League model
   - Set league_name and join_code
   - Add to database session

5. **Create Player for Creator** (line 59):
   - Call `LeagueService.join_league()` with creator's username
   - This creates a Player record and sets as commissioner

6. **Commit Transaction** (line 60)

7. **Return League** (line 61):
   - Return league object with all details

---

## Database Schema

### League Model

**File**: `app/models/leagueModel.py`

**Fields**:
- `id` (Integer, PK): Auto-incrementing unique identifier
- `league_name` (String, Unique): Display name for league
- `join_code` (String, Unique): 9-character code for joining
- `commissioner_id` (Integer, FK): References Player.id

**Relationships**:
- `commissioner`: One-to-one with Player (the league manager)
- `league_players`: One-to-many with Player (all players in league)
- `league_games`: One-to-many with Game (all games in league)

**Unique Constraints**:
- `league_name`: Must be globally unique
- `join_code`: Must be globally unique

### Player Model

**File**: `app/models/playerModel.py`

**Fields**:
- `id` (Integer, PK): Auto-incrementing ID
- `name` (String): User's email (from username)
- `league_id` (Integer, FK): References League.id
- `points` (Float, default=0): Total points accumulated

**Relationships**:
- `league`: Many-to-one with League
- `user`: Many-to-one with User
- `prop_selections`: One-to-many with PlayerPropSelection

**Note**: Same user can be a Player in multiple leagues (different Player records)

---

## Join Code Generation

**Algorithm** (`leagueService.py:47-52`):

1. Generate random string of 9 characters from `[A-Z0-9]`
2. Check if code already exists in database
3. If exists, regenerate (loop until unique)
4. Return unique code

**Probability of Collision**: Very low with 36^9 possible combinations

**Format**: Uppercase letters and numbers only (e.g., "A7X9K2M4P")

---

## Commissioner Assignment

**Process**:

1. When league is created, creator's username is passed to `join_league()`
2. `join_league()` creates a Player record for the creator
3. The Player's ID is set as `league.commissioner_id`
4. This Player has special privileges (can create games, grade, delete league)

**Code**: `leagueService.py:59`

```
LeagueService.join_league(username, leagueName)
```

This function (defined at `leagueService.py:63-119`) handles:
- Creating Player record
- Setting as commissioner if first player
- Adding to league's player list

---

## Frontend Integration

### Create League Form

**Example**:
```javascript
const createLeague = async (leagueName, username) => {
  const response = await fetch('http://localhost:5000/create_league', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include',  // Required for session auth
    body: JSON.stringify({
      leagueName: leagueName,
      username: username
    })
  });

  if (response.ok) {
    const data = await response.json();
    console.log('Join code:', data.league.join_code);
    // Display join code to user
    // Redirect to league home page
  } else {
    const error = await response.json();
    alert(error.description);
  }
};
```

### Displaying Join Code

**Important**: The join code should be prominently displayed to the creator so they can share it with others.

**UI Suggestions**:
- Show in success modal after creation
- Display on league home page
- Provide copy-to-clipboard button
- Allow regeneration if needed

---

## Validation Rules

### League Name

**Rules**:
- Cannot be empty
- Must be unique across all leagues
- No length limit (String type in database)

**Validation Location**: `leagueService.py:38-41`

### Username

**Rules**:
- Must match authenticated session user
- User must exist in database

**Validation Location**: `leagueService.py:44-46`

---

## Common Errors

### 1. "League name already exists"

**Cause**: Another league with same name exists

**Solution**: Choose a different name

**Prevention**: Frontend can check availability before submission

---

### 2. "User does not exist"

**Cause**: Username doesn't match any User record

**Solution**:
- Ensure user is logged in
- Verify username in session matches User table

**Debug**: Check `/check_logged_in` endpoint returns valid username

---

### 3. "League name cannot be empty"

**Cause**: Empty string or null sent for league name

**Solution**: Add frontend validation to require league name

---

### 4. Duplicate join codes (rare)

**Cause**: Random code collision

**Solution**: System automatically regenerates (lines 50-52)

**Monitoring**: Log if this occurs frequently (indicates random generator issue)

---

## Related Workflows

- [Join League](./league-join.md) - Players joining via join code
- [Delete League](./league-delete.md) - Removing a league
- [Get League Info](./league-info.md) - Retrieving league details

---

## Security Considerations

1. **Authentication Required**: Only logged-in users can create leagues
2. **Username Verification**: Username must match session user
3. **Unique Constraints**: Database enforces league name and join code uniqueness
4. **Commissioner Privileges**: Only commissioner can create games and grade

---

## Business Logic

### Why Create Player Record for Creator?

The creator needs to participate in the league, so they get a Player record just like anyone who joins. This keeps the data model consistent:
- All league participants are Players
- Commissioner is just a Player with elevated privileges
- Same user can be in multiple leagues (different Player records)

### Why Unique Join Codes?

Join codes must be globally unique (not just per-league) to:
- Avoid confusion when joining
- Allow for future features (global join code search)
- Prevent accidental joins to wrong league

---

*Last Updated: January 2026*

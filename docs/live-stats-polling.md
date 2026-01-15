# ESPN Live Stats Polling Workflow

## Overview

The system can automatically fetch live statistics from ESPN's API during NFL games and update prop values in real-time. This enables automatic grading based on actual game results without manual input from the League Manager.

## Architecture

```
APScheduler → poll_all_active_games() (every 30 seconds)
    → Find all games with external_game_id and not completed
    → For each game:
        → Fetch ESPN game data
        → Update team scores (Winner/Loser props)
        → Update player stats (Over/Under props)
        → Mark game completed if final
        → Auto-grade if completed
```

## Key Components

### Scheduler Service

**File**: `app/services/game/schedulerService.py`

**Purpose**: Manages APScheduler instance for polling

**Initialization** (`schedulerService.py:15-42`):
- Creates BackgroundScheduler instance
- Configures jobstore (in-memory)
- Sets timezone to US/Eastern
- Starts scheduler

**Job Registration** (`schedulerService.py:44-68`):
- Adds `poll_all_active_games` job
- Runs every 30 seconds
- Prevents duplicate jobs

**Shutdown** (`schedulerService.py:70-80`):
- Gracefully stops scheduler
- Called on app shutdown

---

### Live Stats Service

**File**: `app/services/game/liveStatsService.py`

**Main Functions**:

1. **poll_all_active_games()** (lines 14-50):
   - Entry point called by scheduler
   - Queries all games where `is_completed = False` AND `external_game_id IS NOT NULL`
   - Calls `update_game_from_espn()` for each game
   - Handles errors gracefully (continues to next game on failure)

2. **update_game_from_espn()** (lines 52-131):
   - Fetches game data from ESPN API
   - Updates Winner/Loser prop scores
   - Updates Over/Under prop current values
   - Marks game completed if status is "STATUS_FINAL"
   - Auto-grades completed games

3. **get_espn_game_data()** (lines 133-164):
   - Makes HTTP request to ESPN scoreboard API
   - Parses JSON response
   - Returns game object or None if not found

---

## ESPN API Integration

### Endpoint

```
GET http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
```

**Query Parameters**:
- `dates`: YYYYMMDD format (optional, defaults to today)

**Response Structure**:
```json
{
  "events": [
    {
      "id": "401547638",
      "name": "Los Angeles Rams at Carolina Panthers",
      "status": {
        "type": {
          "name": "STATUS_SCHEDULED",
          "completed": false
        }
      },
      "competitions": [
        {
          "competitors": [
            {
              "team": {
                "abbreviation": "LAR",
                "displayName": "Los Angeles Rams"
              },
              "score": "28",
              "homeAway": "away"
            },
            {
              "team": {
                "abbreviation": "CAR",
                "displayName": "Carolina Panthers"
              },
              "score": "24",
              "homeAway": "home"
            }
          ],
          "competitors": [...],  // Team data
          "status": {
            "type": { "completed": false }
          }
        }
      ]
    }
  ]
}
```

---

## Database Fields Used

### Game Model

**external_game_id** (String):
- ESPN's game ID (e.g., "401547638")
- If NULL, game won't be polled
- Set during game creation

**is_completed** (Boolean):
- False: Game ongoing or upcoming
- True: Game finished, stop polling
- Set automatically when ESPN status is "STATUS_FINAL"

### Winner/Loser Prop

**team_a_id** (String): ESPN team abbreviation (e.g., "LAR")

**team_b_id** (String): ESPN team abbreviation (e.g., "CAR")

**team_a_score** (Integer): Live score for team A

**team_b_score** (Integer): Live score for team B

**team_a_name** (String): Display name (e.g., "Los Angeles Rams")

**team_b_name** (String): Display name (e.g., "Carolina Panthers")

### Over/Under Prop

**player_id** (String): ESPN player ID (e.g., "12483")

**stat_type** (String): Type of stat to track

**current_value** (Float): Live stat value

**line_value** (Float): Over/under threshold

---

## Stat Type Mapping

**Supported stat_type Values**:

| stat_type | ESPN API Path | Description |
|-----------|---------------|-------------|
| passing_yards | statistics[].stats[0] | Passing yards |
| passing_tds | statistics[].stats[1] | Passing touchdowns |
| passing_interceptions | statistics[].stats[2] | Interceptions thrown |
| passing_completions | Custom calculation | Completions (from C/ATT) |
| rushing_yards | statistics[].stats[4] | Rushing yards |
| rushing_tds | statistics[].stats[5] | Rushing touchdowns |
| receiving_yards | statistics[].stats[6] | Receiving yards |
| receiving_tds | statistics[].stats[7] | Receiving touchdowns |
| receiving_receptions | statistics[].stats[8] | Receptions |
| scrimmage_yards | Custom calculation | Rushing + Receiving yards |

**ESPN Statistics Array Indices**:
- [0]: Passing Yards (C/ATT, YDS, TD)
- [1]: Rushing (CAR, YDS, TD)
- [2]: Receiving (REC, YDS, TD)
- etc.

**Code Location**: `liveStatsService.py:166-245` (helper functions for stat extraction)

---

## Update Flow

### 1. Score Updates

**Process** (`liveStatsService.py:74-102`):

1. Find Winner/Loser props with matching team IDs
2. Extract scores from ESPN data
3. Update `team_a_score` and `team_b_score`
4. Commit to database

**Team Matching**:
- Uses `team_a_id` and `team_b_id` to match ESPN competitors
- Handles home/away team positioning
- Updates correct team score regardless of order

### 2. Player Stat Updates

**Process** (`liveStatsService.py:104-119`):

1. Find Over/Under props with `player_id` and `stat_type`
2. Fetch player stats from ESPN boxscore
3. Extract specific stat based on `stat_type`
4. Update `current_value`
5. Commit to database

**Stat Extraction** (lines 166-245):
- Helper functions for each stat type
- Parses ESPN's nested statistics structure
- Handles missing data gracefully

---

## Auto-Grading Trigger

**Location**: `liveStatsService.py:121-129`

**Condition**:
```python
if espn_game_status == "STATUS_FINAL" and not game.is_completed:
    # Mark game as completed
    game.is_completed = True
    db.session.commit()

    # Auto-grade props
    GradeGameService.auto_grade_props_from_live_data(game)

    # Grade game (award points)
    GradeGameService.grade_game(game.id)
```

**auto_grade_props_from_live_data()** (`gradeGameService.py:29-68`):
- Sets `correct_answer` for Winner/Loser props based on scores
- Sets `correct_answer` for Over/Under props based on current_value vs line_value
- Does NOT award points (just sets correct answers)

**grade_game()** (`gradeGameService.py:90-182`):
- Awards points to players based on correct answers
- Checks prop selections for optional props
- Updates player.points

---

## Polling Schedule

### Frequency

**Interval**: Every 30 seconds

**Configuration**: `schedulerService.py:57`

### Active Games Query

**Query** (`liveStatsService.py:22-26`):
```python
Game.query.filter(
    Game.is_completed == False,
    Game.external_game_id.isnot(None)
).all()
```

**Criteria**:
- Game not marked completed
- Has ESPN game ID

**Performance**: Efficient query with indices on `is_completed` and `external_game_id`

---

## Error Handling

### ESPN API Failures

**Handling** (`liveStatsService.py:40-46`):
```python
try:
    update_game_from_espn(game)
except Exception as e:
    print(f"Error polling game {game.id}: {str(e)}")
    # Continue to next game
```

**Behavior**: One failed game doesn't stop polling other games

### Missing Data

**Player Not Found** (`liveStatsService.py:218-220`):
- Returns None
- Prop's `current_value` not updated
- No error thrown

**Stat Not Available**:
- Returns 0 or None
- Prop remains at last known value

---

## Scheduler Initialization

### Local Development

**File**: `run.py:35-42`

```python
if __name__ == "__main__":
    from app.services.game.schedulerService import SchedulerService
    SchedulerService.initialize_scheduler(app)
    app.run(debug=True)
```

**Note**: Scheduler started before Flask runs

### Production (Gunicorn)

**File**: `gunicorn_config.py:10-21`

```python
def post_fork(server, worker):
    # Each worker process initializes its own scheduler
    with app.app_context():
        SchedulerService.initialize_scheduler(app)
```

**Why post_fork**: Each worker needs separate scheduler instance

---

## Configuration

### Environment Variables

**None Required**: ESPN API is public, no auth needed

### Timezone

**Setting**: `schedulerService.py:25`
```python
timezone=pytz.timezone('US/Eastern')
```

**Reason**: NFL games use ET/EDT timezone

---

## Manual Polling Endpoint

**GET** `/poll_game/<int:game_id>`

**Purpose**: Manually trigger update for specific game

**Controller**: `liveStatsController.py:10-32`

**Usage**:
```http
GET /poll_game/123 HTTP/1.1
```

**Response**:
```json
{
  "message": "Game data updated successfully"
}
```

**Use Cases**:
- Testing during development
- Force update if scheduler fails
- Debugging stat updates

---

## Frontend Integration

### Displaying Live Stats

**Polling from Frontend**: NOT RECOMMENDED

**Why**: Backend already polls every 30 seconds

**Instead**: Frontend fetches game data periodically (every 30-60 seconds)

**Example**:
```javascript
const fetchGameData = async () => {
  const response = await fetch(`${apiUrl}/get_game_by_id?game_id=${gameId}`, {
    credentials: 'include'
  });

  const game = await response.json();
  // Update UI with latest scores and stats
};

// Poll every 30 seconds
setInterval(fetchGameData, 30000);
```

---

## Common Issues

### 1. Stats Not Updating

**Possible Causes**:
- `external_game_id` not set
- `player_id` doesn't match ESPN's ID
- `stat_type` misspelled or unsupported
- Game marked as completed

**Debug**:
1. Check `game.external_game_id` is populated
2. Verify `prop.player_id` matches ESPN
3. Check scheduler is running (logs should show polling)
4. Manually call `/poll_game/{id}` to test

---

### 2. Duplicate Grading

**Cause**: Scheduler running in multiple worker processes

**Prevention**: Check in `auto_grade_props_from_live_data` if already graded

**Current Behavior**: `is_completed` flag prevents re-polling after game ends

---

### 3. Wrong Stats Pulled

**Cause**: Incorrect `stat_type` or `player_id`

**Solution**:
- Verify `stat_type` matches supported values
- Check ESPN player ID is correct (not team ID)

---

### 4. Scheduler Not Starting

**Symptoms**: No polling logs, stats never update

**Check**:
1. `SchedulerService.initialize_scheduler()` called
2. No errors in startup logs
3. Jobs registered with scheduler

**Debug**: Add logging to `poll_all_active_games()`

---

## Testing

### Manual Testing

1. Create game with `external_game_id`
2. Wait for game to start
3. Check logs for polling activity
4. Verify scores update in database
5. Wait for game to complete
6. Verify auto-grading triggered

### Simulating Live Game

Use manual polling endpoint:
```bash
curl http://localhost:5000/poll_game/123
```

Check database after each call for updated values

---

## Performance Considerations

### API Rate Limiting

**ESPN API**: No documented rate limit

**Current Load**:
- 1 request per game per 30 seconds
- Average: 10-20 games polling simultaneously
- ~40 requests/minute during peak

**Optimization**: Could batch multiple games into single scoreboard request

### Database Load

**Writes per Poll**:
- 1-10 prop updates per game
- Score updates (2 props per game average)
- Stat updates (2-8 props per game average)

**Total**: ~100-200 DB writes per minute during peak

---

## Related Workflows

- [Create Game](./game-create.md) - Setting external_game_id
- [Auto-Grading](./grading-auto.md) - Automatic correct answer setting
- [Manual Grading](./grading-manual.md) - Alternative to auto-grading

---

*Last Updated: January 2026*

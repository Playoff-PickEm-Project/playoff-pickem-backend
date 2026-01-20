# Playoff Pickem Backend Documentation

## Overview

This documentation provides comprehensive guides for all backend workflows in the Playoff Pickem application. Each workflow is documented with architecture details, API endpoints, request/response formats, code references, and common errors.

## Architecture

The backend follows a layered architecture pattern:

```
Controllers (HTTP Layer)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Models (Database Schema)
```

### Technology Stack

- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Google OAuth 2.0 (via Authlib)
- **Migrations**: Alembic (Flask-Migrate)
- **External API**: ESPN API for live sports data

### Project Structure

```
app/
├── controllers/     # HTTP request handlers (routes)
├── services/        # Business logic layer
├── repositories/    # Database queries
├── models/          # SQLAlchemy database models
├── validators/      # Input validation functions
└── utils/           # Helper utilities

migrations/          # Database migration scripts
tests/              # Unit and integration tests
```

## Workflow Documentation

### User & Authentication
- [User Authentication](./user-authentication.md) - Google OAuth login/logout flow
- [User Registration](./user-registration.md) - First-time user setup

### League Management
- [Create League](./league-create.md) - Creating a new league
- [Join League](./league-join.md) - Joining via join code
- [Delete League](./league-delete.md) - Removing a league
- [Get League Info](./league-info.md) - Retrieving league details

### Game Management
- [Create Game](./game-create.md) - Creating a game with props
- [Edit Game](./game-edit.md) - Updating game details
- [Delete Game](./game-delete.md) - Removing a game
- [View Games](./game-list.md) - Listing games in a league

### Prop Management
- [Create Winner/Loser Props](./prop-winner-loser.md) - Team selection props
- [Create Over/Under Props](./prop-over-under.md) - Statistical threshold props
- [Create Variable Option Props](./prop-variable-option.md) - Multiple choice props
- [Create Anytime TD Props](./prop-anytime-td.md) - Player touchdown scorer props
- [Add Prop to Existing Game](./prop-add-to-game.md) - Adding props after game creation
- [Delete Props](./prop-delete.md) - Removing props from a game
- [Edit Props](./prop-edit.md) - Modifying existing props

### Prop Selection (NEW FEATURE)
- [Prop Selection Workflow](./prop-selection.md) - Players choosing which props to answer
- [Mandatory vs Optional Props](./prop-mandatory-optional.md) - Prop type distinction

### Answering Props
- [Answer Props](./prop-answer.md) - Players submitting answers
- [View Player Answers](./prop-view-answers.md) - Retrieving submitted answers

### Grading
- [Manual Grading](./grading-manual.md) - Commissioner sets correct answers
- [Auto-Grading](./grading-auto.md) - Automatic grading from live data
- [Grading with Prop Selection](./grading-prop-selection.md) - How selection affects grading

### Live Stats
- [ESPN Live Polling](./live-stats-polling.md) - Fetching real-time game data
- [Update Game Stats](./live-stats-update.md) - Updating props with live values

### Player & Standings
- [View Standings](./standings.md) - League leaderboard
- [Player Stats](./player-stats.md) - Individual player performance

## Common Patterns

### Error Handling

All endpoints follow this error response format:

```json
{
  "description": "Error message here",
  "error": "Error type (optional)"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad request (validation error)
- `401` - Unauthorized
- `404` - Resource not found
- `500` - Internal server error

### Request Authentication

Most endpoints require authentication via session cookies:
- Must include `credentials: 'include'` in frontend fetch requests
- Session established via Google OAuth login
- Username stored in session for authorization checks

### Database Transactions

- Services use `db.session.commit()` to persist changes
- Errors trigger automatic rollback
- Multiple operations in a service are wrapped in single transaction

## Quick Reference

### Key Models

- **User**: Authentication and profile
- **League**: Competition container
- **Player**: User's participation in a league
- **Game**: Event with props
- **WinnerLoserProp**: Team selection prop
- **OverUnderProp**: Statistical threshold prop
- **VariableOptionProp**: Multiple choice prop
- **AnytimeTdProp**: Player touchdown scorer prop
- **PlayerPropSelection**: Tracks which props a player selected
- **[Type]Answer**: Player's answer to a prop

### Key Controllers

- `usersController.py` - Authentication & user management
- `leagueController.py` - League operations & game creation
- `gameController.py` - Game operations & prop management
- `propController.py` - Prop selection & answering
- `liveStatsController.py` - ESPN data integration

### Key Services

- `userService.py` - User operations
- `leagueService.py` - League & player management
- `gameService.py` - Game creation & prop creation
- `gradeGameService.py` - Grading logic
- `propService.py` - Prop selection logic
- `liveStatsService.py` - ESPN API integration

## Development Tips

### Adding a New Endpoint

1. Define route in appropriate controller
2. Implement business logic in service
3. Add database queries in repository (if needed)
4. Update validators for input validation
5. Add tests in `tests/` directory
6. Document in this docs folder

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_prop_selection_grading.py

# Run with verbose output
python -m pytest -v
```

### Database Migrations

```bash
# Create migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Check current migration version
flask db current
```

## Troubleshooting

See individual workflow docs for specific error scenarios. Common issues:

1. **Session/Authentication Issues**: Check CORS configuration and credentials
2. **Database Errors**: Verify migrations are up to date with `flask db current`
3. **Foreign Key Violations**: Check cascade delete configurations in models
4. **Unique Constraint Violations**: Ensure unique fields (league names, join codes) are properly validated

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [ESPN API Documentation](http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard)

---

*Last Updated: January 2026*
*For questions or contributions, please open an issue on GitHub.*

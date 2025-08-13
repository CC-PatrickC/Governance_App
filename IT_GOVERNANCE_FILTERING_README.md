# IT Governance Scoring Group Filtering

This feature allows users in the "IT Governance Scoring" group to only see and score IT Governance type projects, while other scoring users can see all project types.

## How It Works

### Group-Based Access Control

1. **IT Governance Scoring Group**: Users in this group can only see and score projects with `project_type = 'it_governance'`
2. **Staff Users**: Staff users (is_staff=True) can see all project types regardless of group membership
3. **Regular Scoring Users**: Users in the "Scoring Group" can see all project types

### Views Affected

The following views now include group-based filtering:

- `project_scoring_list` - Main scoring page
- `project_final_scoring_list` - Final scoring page  
- `project_scoring` - Individual project scoring
- `project_final_scoring` - Individual final scoring
- `project_final_scoring_details` - Scoring details view
- `project_scoring_details_modal` - Modal scoring details

### Access Control

Each view checks if the user is in the "IT Governance Scoring" group and not a staff user. If so, it filters projects to only show IT Governance projects and prevents access to other project types.

## Management Commands

### Create the Group
```bash
python manage.py create_it_governance_group
```

### Add Users to the Group
```bash
python manage.py add_user_to_it_governance <username>
```

### List Users in the Group
```bash
python manage.py list_it_governance_users
```

## User Experience

### For IT Governance Scoring Users
- Only see IT Governance projects in scoring lists
- Cannot access other project types directly via URL
- See a notice: "You are viewing IT Governance projects only"
- Get error messages if trying to access unauthorized projects

### For Staff Users
- See all project types regardless of group membership
- See a notice: "You have access to all project types as an administrator"

### For Regular Scoring Users
- See all project types
- See a notice: "You have access to all project types"

## Testing

Run the test script to verify the implementation:
```bash
python test_group_filtering.py
```

## Implementation Details

### New Functions
- `is_it_governance_scoring_user(user)` - Checks if user is in IT Governance Scoring group

### Template Updates
- Added group-based notices to scoring list templates
- Shows appropriate messages based on user's group membership

### Security
- Access control at both list and individual project levels
- Prevents direct URL access to unauthorized projects
- Returns appropriate error messages and redirects

## Example Usage

1. Create the group:
   ```bash
   python manage.py create_it_governance_group
   ```

2. Add a user to the group:
   ```bash
   python manage.py add_user_to_it_governance john_doe
   ```

3. The user will now only see IT Governance projects when they log in and access the scoring pages.

## Troubleshooting

- If a user can't see any projects, check if they're in the correct group
- If a user sees all projects when they shouldn't, check if they're marked as staff
- Use the test script to verify group membership and access rights 
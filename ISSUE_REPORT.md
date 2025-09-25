# Governance App - Deployment Issue Report

## Issue Summary
**Date:** September 24, 2025  
**Issue:** "Error loading edit form" when attempting to edit projects in Azure deployment  
**Status:** ✅ RESOLVED  

## Problem Description
Users were unable to edit projects from the "My Governance" page in the Azure-deployed application. Clicking on any project to edit resulted in a generic "Error loading edit form" message.

## Root Cause Analysis
The issue was caused by missing database migrations in the Azure PostgreSQL database. Specifically:

- **Missing Table:** `projects_triagechange` 
- **Missing Migration:** `0034_add_triage_change_model.py`
- **SQL Error:** `relation "projects_triagechange" does not exist`

## Diagnostic Process
1. **Enhanced Error Handling:** Added detailed error reporting to capture the exact error
2. **Improved Logging:** Implemented comprehensive logging to trace the issue
3. **Error Analysis:** The enhanced error message revealed the missing database table
4. **Migration Check:** Identified that recent migrations were not applied to Azure database

## Solution Implemented
Ran database migrations on Azure App Service:
```bash
# Connected to Azure App Service via SSH
python manage.py migrate
```

## Error Message Before Fix
```
Error loading edit form

Error details: Network response was not ok: 500 Internal Server Error. 
Response: {"error": "Error loading form: relation \"projects_triagechange\" does not exist
LINE 1: ...by_id\", \"projects_triagechange\".\"changed_at\" FROM \"projects_...
                                                              ^
"}

Project ID: 4
URL: /4/edit-form/
```

## Error Message After Fix
✅ Edit forms now load successfully and users can edit projects without issues.

## Prevention Measures
1. **Deployment Checklist:** Ensure migrations are run as part of deployment process
2. **Enhanced Monitoring:** Keep the improved error handling for future issues
3. **Documentation:** Created troubleshooting guide for similar issues

## Technical Impact
- **Issue Duration:** Temporary (resolved same day)
- **User Impact:** Edit functionality was temporarily unavailable
- **Data Impact:** None - no data was lost or corrupted
- **Resolution Time:** < 30 minutes after identifying root cause

---
*Report prepared by: Development Team*  
*Date: September 24, 2025*
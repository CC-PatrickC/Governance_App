# Azure Deployment Troubleshooting Guide

## Issue
"Error loading edit form" when trying to edit projects from the "My Governance" page in the Azure-deployed app.

## Changes Made for Debugging

### 1. Added Logging Configuration
- Added comprehensive logging to `project_intake/settings.py`
- Logs will be written to `debug.log` file
- Added detailed logging to the `project_update_form_ajax` view

### 2. Improved Error Handling
- Enhanced JavaScript error handling in `my_governance.html` to show detailed error messages
- Added console logging to capture response status and headers
- Better error display in the modal

### 3. Temporarily Enabled DEBUG Mode
- Set `DEBUG = True` in settings.py for troubleshooting
- **IMPORTANT**: Remove this before final deployment

### 4. Added Test Endpoint
- Created `/test-ajax/` endpoint to test basic AJAX functionality
- This can be used to verify if AJAX requests work in Azure environment

## Troubleshooting Steps

### Step 1: Check Logs
1. Deploy the updated code to Azure
2. Try to edit a project and reproduce the error
3. Check the Azure logs for detailed error messages from the Django application

### Step 2: Test Basic AJAX
1. Open browser developer console on the Azure app
2. Run: `fetch('/test-ajax/').then(r => r.json()).then(console.log)`
3. This will test if basic AJAX requests work

### Step 3: Test Specific Edit Form Request
1. In the browser console, run:
```javascript
fetch('/1/edit-form/')  // Replace 1 with an actual project ID
  .then(response => {
    console.log('Status:', response.status);
    console.log('Headers:', response.headers);
    return response.text();
  })
  .then(text => console.log('Response:', text))
  .catch(error => console.error('Error:', error));
```

### Step 4: Check Network Tab
1. Open browser Developer Tools > Network tab
2. Try to edit a project
3. Look for the `edit-form` request and check:
   - Request URL
   - Response status
   - Response headers
   - Response body

## Common Azure Deployment Issues

### 1. Database Connection
- Ensure Azure PostgreSQL allows connections from the App Service
- Check connection string environment variables
- Verify firewall rules

### 2. Static Files
- Ensure static files are collected and served properly
- Check if CSS/JS files are loading correctly

### 3. Authentication/CSRF
- Verify CSRF token is being passed correctly
- Check if user authentication is working

### 4. Environment Variables
- Ensure all required environment variables are set in Azure App Service
- Check that .env file values match Azure configuration

## Next Steps

1. Deploy the updated code with debugging enabled
2. Reproduce the error and check logs
3. Use the troubleshooting steps above to identify the root cause
4. Once identified, implement the fix and remove the DEBUG = True setting

## Files Modified
- `project_intake/settings.py` - Added logging configuration and DEBUG
- `projects/views.py` - Enhanced error logging and added test endpoint
- `projects/urls.py` - Added test endpoint URL
- `projects/templates/projects/my_governance.html` - Improved error handling
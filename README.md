# desk-dash
## python project to help me keep track of my spending 

Using python and crontab, update my desktop background with a bar chart reflecting this month's current spending in a given category.
This project takes advantage of my "dolla-dolla" project by assuming all my spending is recorded in Google Sheets and backed up in a local SQLite database.

Crontab (update every 4 hours):
```
0 */4 * * * python /Users/jack/Documents/projects/22-dash/dash.py
```

The system is set to change the desktop picture every few minutes.
The folder for backgrounds only ever has the most current image in it, so the system only changes backgrounds when there's a new image with a new name.

Licensed under the [MIT License](LICENSE).

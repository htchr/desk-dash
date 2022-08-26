# desk-dash
#### python project to help me keep track of my spending 
---

Using python and crontab, update my desktop background with a bar chart reflecting this month's current spending in a given category.
This project takes advantage of my "dolla-dolla" project by assuming all my spending is recorded in Google Sheets and backed up in a local SQLite database.

Crontab (update every 4 hours):
```
0 */4 * * * python /Users/jack/Documents/projects/22-dash/dash.py
```

Licensed under the [MIT License](LICENSE).

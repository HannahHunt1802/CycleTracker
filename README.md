# Cycle Tracker
A web app that allows users to track their menstrual cycle.

------------
## Features

- User authentication (login/registration)
- Dashboard UI
- Edit account data (change password, email, account deletion, cycle info)
- Period logging + editing
- Cycle prediction logic
- Interactive calendar view

#### Tech Stack: Python, Flask, SQLite, FullCalendar.js, HTML, CSS

## Installation Instructions:
1. Download or clone the project
2. Install dependencies: 
``pip install -r requirements.txt``
3. Run the app: ``python run.py``
4. Open link printed on console (e.g. ``http://127.0.0.1:5000/``)

---------
### Note on Reused Templates
This project was built on a short deadline for a placement application, so I have
reused some of my existing code to speed up progress:
- The authentication boilerplate (login + register) comes from a Flask project I am currently building
at university.
- The CSS+HTML structure base is pulled from my personal project (PlantApp) because it was easy to adapt 
and I like the styling.

All period-tracking logic - models, prediction logic, calendar integration, APIs, etc - 
was written fresh for this project.

### Future Improvements
- Cycle phases and analytics (e.g. follicular, luteal)
- Birth control features (e.g. mark placebo week)
- Symptom and mood tracking (e.g. flow, discharge, activity)
- Improve frontend-backend wiring for all UI actions
- Visual improvements (day/night mode - utilise my sun/moon assets and create more custom icons)
- Data export of cycle history

### Screenshots
Here are the designs I made in Figma before creating the app:

<img src="design-screenshots/SignInPage.png" width="400">
<img src="design-screenshots/Dashboard.png" width="400">
<img src="design-screenshots/Calendar.png" width="400">
<img src="design-screenshots/Settings.png" width="400">
<img src="design-screenshots/Cycle Statistics.png" width="400">
<img src="design-screenshots/NightMode.png" width="400">

And here are some screenshots from after development:

<img src="design-screenshots/LiveRegister.png" width="400">
<img src="design-screenshots/LiveLogin.png" width="400">
<img src="design-screenshots/LiveDashboard.png" width="400">
<img src="design-screenshots/LiveCalendar.png" width="400">
<img src="design-screenshots/LiveAccount.png" width="400">
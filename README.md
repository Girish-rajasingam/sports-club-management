# Sports Club Management System

A web application to manage a sports club: members, coaches, sports, enrollments and monthly fee
payments, with a dashboard and a pending-fees report.

**Tech stack:** Python (Flask), MySQL, HTML/CSS

## Features
- **Dashboard** – total members, coaches and sports, total fees collected, and enrollments per sport
- **Full CRUD** (add / view / edit / delete) for Members, Coaches, Sports, Enrollments and Payments
- **Search** on every list page
- **Pending Fees Report** – for any month, shows what each member owes, has paid and still has pending,
  with the total outstanding amount
- Dropdown forms that pull data from related tables (e.g. choose a coach for a sport)

## Database design
Five related tables:

| Table | Purpose | Linked to |
|---|---|---|
| `coaches` | Coach details | – |
| `sports` | Sport name, monthly fee | `coaches` |
| `members` | Member details | – |
| `enrollments` | Which member plays which sport | `members`, `sports` |
| `payments` | Fee payments by month | `members` |

Foreign keys keep the data consistent (for example, deleting a member also removes their enrollments
and payments).

## How to run
1. Install Python 3 and MySQL Server.
2. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
3. Create the database and sample data:
   ```
   mysql -u root -p < schema.sql
   ```
4. Set your MySQL password (skip if your root user has none):
   - Windows: `set DB_PASS=yourpassword`
   - Mac / Linux: `export DB_PASS=yourpassword`
5. Start the app:
   ```
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

## Project structure
```
app.py            Flask routes and database logic
schema.sql        Table definitions and sample data
templates/        HTML pages (dashboard, lists, forms, pending report)
requirements.txt  Python dependencies
```

## What I learned
Designing a relational database, writing SQL queries with joins and aggregation, connecting Python to
MySQL, and building a simple web interface for data entry and reporting.

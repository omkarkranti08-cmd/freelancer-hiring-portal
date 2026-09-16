# Freelancer Hiring Portal

A Django-based web platform connecting clients with freelancers for project hiring and management.

## Features
- User accounts for clients and freelancers
- Post and browse freelance projects
- Freelancer profiles and hiring management

## Tech Stack
- Python / Django
- SQLite (development database)
- HTML/CSS templates

## Setup Instructions

1. Clone the repository: git clone https://github.com/omkarkranti08-cmd/freelancer-hiring-portal.git

2. Move into the project folder: cd freelancer-hiring-portal

3. Create a virtual environment: python -m venv venv

4. Activate the virtual environment: venv\Scripts\activate

5. Install dependencies: pip install -r requirements.txt

6. Run migrations: python manage.py migrate

7. Start the development server: python manage.py runserver

8. Open your browser at http://127.0.0.1:8000/

## Project Structure
- accounts/ – user authentication and profiles
- freelancer_portal/ – core project settings and app logic
- templates/ – HTML templates

## License
This project is open source and available for learning purposes.

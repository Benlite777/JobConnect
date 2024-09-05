
# JobConnect

## Overview

**JobConnect** is an online job portal that connects job seekers with recruiters. The platform allows job seekers to create profiles, search for available jobs, and apply for positions. Recruiters can post job openings, manage applications, and view candidates’ profiles. The system is built using **Django** and features an intuitive interface for both job seekers and recruiters.

## Features

### For Job Seekers:
- **Profile Creation**: Users can register, create profiles, and manage their information.
- **Job Search**: Browse and filter job listings based on job type, location, and industry.
- **Application Submission**: Apply for jobs directly from the platform and track application status.

### For Recruiters:
- **Job Posting**: Post job vacancies with detailed job descriptions.
- **Candidate Management**: View applicants, shortlist candidates, and track application statuses.
- **Dashboard**: Manage and review job posts, applications, and candidate profiles from an admin interface.

## Tech Stack
- **Frontend**: HTML, CSS, Bootstrap
- **Backend**: Django Framework
- **Database**: SQLite (can be changed to PostgreSQL or MySQL for production)
- **Deployment**: AWS EC2 or any other cloud platform
- **Other Tools**: 
  - Microsoft Office Suite
  - GitHub for version control
  - Canva for graphics

## Installation

### Prerequisites
- Python 3.x
- Django 3.x
- Git

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jobconnect.git
   cd jobconnect
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the site at `http://127.0.0.1:8000`.

## Usage

- To register as a **Job Seeker** or **Recruiter**, navigate to the appropriate registration page.
- Recruiters can manage job postings and applications via their dashboard.
- Job Seekers can search for available jobs and submit applications directly through the platform.


---

Feel free to modify and expand upon this as needed!

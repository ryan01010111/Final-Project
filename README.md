# Center Line

## Aviation Training Management and Tracking for Schools, Instructors and Students

#### Tech Stack:

- Python with Flask
- SQLite
- HTML
- CSS/SASS with Bootstrap
- JavaScript

#### Feature Breakdown:

### 1. User Accounts

The application features accounts for individual users. It supports accounts for both instructors and students. Each
user's account is used to track and store flight training data that is relevant to the user and the user's students/instructors.

**Features**:

- Account registration with choice of role (instructor/student)
- Profile page
  - view personal data
  - view and manage students' data and settings
  - change view mode (see below)

### 2. Student and Instructor View Modes

The application user's view and interface will depend on their role. If a user is simultaneously an instructor and a current
student, the user has the option of changing view modes (from instructor to student, and vice-versa).

**Features**:

- change view mode via a button on the user's profile page

### 3. Dashboard

The dashboard is, by default, the first interface that every user (instructor and student) sees when they are logged in. The
dashboard is meant to provide a convenient view of the most in-demand data for a given user.

**Features**:

- Instructor View - notifications for flight logs of user's students that are awaiting confirmation by the user

- Student View - current training course (see below) - progress in current course (see below) - notifications for user's flight logs that are awaiting confirmation by the user's instructor

### 4. Courses

Courses are the collections of requirements necessary for obtaining a certain license or endorsement.

**Features**:

- each user can be assigned a course by the user's instructor

### 5. Logbook and Flight Logs

The logbook is the user's virtual logbook. This feature stores all flight and flight-training data for each user.

**Features**:

- add new flight log entries
- view all flight logs
- used to calculate progress (see below) in a user's course
- logs must be confirmed by user's instructor to be included in progress calculation
- notes

### 6. Sessions

Sessions are simple records of training sessions. They include the session date, and comments for documentation.

**Features**:

- add and update training session entries
- view all training sessions relevant to user and user's role/view mode

### 7. Students

The Students interface allows instructors to manage individual students.

**Features**:

- add students
- find and view students
- quickly view students' progress
- view students' profiles

### 8. Progress

For each user, if that user is currently assigned a course, that user's progress in their assigned course is calculated. Progress
calculation is based on all of a user's confirmed flight logs.

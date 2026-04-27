# Roommate Match Instructions

This document explains how to run and use the roommate match program.

## Install Dependencies

This project uses **uv** to manage Python dependencies.

1. Install uv using the official installer:

[uv Installation Instructions](https://docs.astral.sh/uv/getting-started/installation/)

2. Install the project dependencies (in terminal):

uv sync

## Running the program

1. Open a terminal
2. Navigate to the project folder /bank/src/
3. Run the CLI:

uv run python main.py

## Tutorial

Admin menu:
- log in using email: admin@campus.edu, password: admin
has options:
- create student
    - enter student information
    - a temporary password will be assigned to that student
    - the student can change this password when they log in
- finalize pairing
    - pairings will show up here when all members of a request have accepted it
    - admin can reject or approve all pairings
    - once approved, a group ID is assigned and the group can be found under the view all groups button

Student menu:
- log in using an email and username in the students.csv file
has options:
- view students/make request
    - students are listed in order from most similar to least similar
    - a student can make a request if they have no requests outgoing or pending
    - a student can only send one request and can only recieve one request
    - click on multiple students to send a request all at once
    - if one person in the request group rejects the request, the request is void and a new request must be made
- view request status
    - view all members of the group and see their status: pending/accepted
- view group status
    - a request becomes a group when all members of the request have accepted
    - once a request becomes a group, the admin has the option to approve or deny this group
- respond to requests
    - see pending requests and accept or reject the request
- change interests
    - click to toggle each of the interests
- change preferences
    - click to toggle each of the preferences
- change password
    - provide old password to change to a new password
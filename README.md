# Library Management System (Python OOP) 🐍

## Project Overview
This is **Project 3** for Group 1, implemented in **Python** and built strictly on the principles of **Object-Oriented Programming (OOP)**.

The system manages library operations, demonstrating key OOP concepts:
* **Classes:** Every entity (`Book`, `User`, `Loan`) is a Class.
* **Encapsulation:** The entire state (`books`, `users`, `next_user_id`) is managed privately within the main `Library` manager class.
* **Composition:** The `User` class is composed of `Loan` objects (the list of books they have taken).
* **Serialization:** Custom methods (`to_dict`) are used to convert objects to JSON for file persistence.

## Core Structure & Methods
The entire program logic is stored within class methods (behavior) and instance variables (data).

| Class | Purpose | Key Method Summary |
| :--- | :--- | :--- |
| **`Book`** | Manages details, copies, and reservation queue. | `to_dict()` |
| **`User`** | Tracks identity and current loans. | `to_dict()` |
| **`Loan`** | Models a transaction/issue record with due dates. | `to_dict()`, Overdue check (`__str__`) |
| **`Library`** | **The Manager Class.** Handles all business logic and persistence. | `add/remove_book/user()`, `borrow/return/reserve_book()`, `overdue_books()`, `generate_report()`, `save/load_to_file()` |

## Getting Started: Installation & Setup 🛠️

1.  **Requirements:** Requires **Python 3.6+**. No external libraries are needed beyond standard Python.
2.  **Run:** Open your terminal in the project directory and run the main file:
    ```bash
    python3 main.py
    ```
    *(The program will attempt to load data from `library_data.json` on startup.)*

## Example of Execution (Full Console Menu)

The main program runs a continuous console menu, allowing the user to manage the library state and check reports.

```bash
$ python3 main.py
[INFO] File library_data.json not found. Starting with empty library.

--- Library Management System Menu ---
1: Add Book
...
0: Exit
Enter your choice: 3

User Name: Alice
[Success] Added user: Alice (ID: 1)

--- Library Management System Menu ---
...
Enter your choice: 1

Book Title: The Martian
Author: Andy Weir
Number of Copies: 2
[Success] Added new book: Book(Title: 'The Martian', Author: Andy Weir, Available: 2/2, Reserved: 0)

--- Library Management System Menu ---
...
Enter your choice: 5

User ID (borrower): 1
Book Title to borrow: The Martian
[Success] Alice borrowed 'The Martian'. Due: 202X-XX-XX

--- Library Management System Menu ---
...
Enter your choice: 8

--- LIBRARY STATUS REPORT ---
Total Unique Titles: 1
Total Book Copies:   2
Available Copies:    1 (50.0% available)
Total Users:         1
Active Loans:        1
Overdue Loans:       0
----------------------------

--- ACTIVE USERS ---
User(Name: Alice, ID: 1, Loans: 1)
  - 'The Martian' (Due: 202X-XX-XX) [Active]
----------------------------

--- Library Management System Menu ---
...
Enter your choice: 0

Saving data before exit...
[SUCCESS] Data saved to library_data.json
Exiting Library Management System. Goodbye!

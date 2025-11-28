import json
import os
from datetime import datetime, timedelta

# --- Configuration ---
FILENAME = "library_data.json"
LOAN_PERIOD_DAYS = 14

# ===============================================
# CORE ENTITY CLASSES (OOP & Serialization)
# ===============================================

class Book:
    """Stores book details, availability, and reservation list."""
    def __init__(self, title, author, total_copies, available_copies=None, reservations=None):
        self.title = title
        self.author = author
        self.total_copies = total_copies
        # Default values for new book; uses saved data when loading
        self.available_copies = available_copies if available_copies is not None else total_copies
        self.reservations = reservations if reservations is not None else []
    
    def __str__(self):
        return (f"Book(Title: '{self.title}', Author: {self.author}, "
                f"Available: {self.available_copies}/{self.total_copies}, "
                f"Reserved: {len(self.reservations)})")

    # Method for JSON serialization (converting object data to a dictionary)
    def to_dict(self):
        return {
            "__class__": "Book",
            "title": self.title,
            "author": self.author,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "reservations": self.reservations
        }

class User:
    """Stores user details and tracks the books they currently hold."""
    def __init__(self, name, user_id, taken_books=None):
        self.name = name
        self.user_id = user_id
        # When loading, 'taken_books' will contain Loan dictionaries (not objects yet)
        self.taken_books = taken_books if taken_books is not None else []
    
    def __str__(self):
        return f"User(Name: {self.name}, ID: {self.user_id}, Loans: {len(self.taken_books)})"

    # Method for JSON serialization
    def to_dict(self):
        return {
            "__class__": "User",
            "name": self.name,
            "user_id": self.user_id,
            "taken_books": [loan.to_dict() for loan in self.taken_books]
        }

class Loan:
    """Links a specific User and a Book; tracks the due date."""
    def __init__(self, user_id, book_title, issue_date_str=None, due_date_str=None):
        self.user_id = user_id
        self.book_title = book_title
        
        # Deserialization: Convert string back to datetime object
        if issue_date_str and due_date_str:
            self.issue_date = datetime.fromisoformat(issue_date_str)
            self.due_date = datetime.fromisoformat(due_date_str)
        # New loan creation
        else:
            self.issue_date = datetime.now()
            self.due_date = self.issue_date + timedelta(days=LOAN_PERIOD_DAYS)
    
    def __str__(self):
        status = "OVERDUE" if datetime.now() > self.due_date else "Active"
        return (f"  - '{self.book_title}' (Due: {self.due_date.strftime('%Y-%m-%d')}) [{status}]")

    # Method for JSON serialization: Date objects must be converted to strings
    def to_dict(self):
        return {
            "__class__": "Loan",
            "user_id": self.user_id,
            "book_title": self.book_title,
            "issue_date_str": self.issue_date.isoformat(),
            "due_date_str": self.due_date.isoformat()
        }


# ===============================================
# MANAGER CLASS (Library - All Business Logic)
# ===============================================

class Library:
    """Manages the collection of all Books, Users, and Loans."""
    def __init__(self):
        # Encapsulated state:
        self.books = {}
        self.users = {}
        self.next_user_id = 1
        
    # --- PRIVATE HELPERS ---
    def _get_user_by_name(self, name):
        """Helper to find a User object by name (case-insensitive)."""
        for user in self.users.values():
            if user.name.lower() == name.lower():
                return user
        return None
    
    def _get_user_by_id(self, user_id):
        """Helper to find a User object by ID."""
        return self.users.get(user_id)

    def _get_book_by_title(self, title):
        """Helper to find a Book object by title."""
        return self.books.get(title)

    # --- CRUD METHODS ---
    def add_book(self, title, author, total_copies):
        """Adds a new book."""
        if title in self.books:
            # If the book already exists, increment copies (instead of error)
            self.books[title].total_copies += total_copies
            self.books[title].available_copies += total_copies
            print(f"[Success] Updated total copies of '{title}' to {self.books[title].total_copies}.")
            return
            
        new_book = Book(title, author, total_copies)
        self.books[title] = new_book
        print(f"[Success] Added new book: {new_book}")

    def remove_book(self, book_title):
        """Removes a book by title if all copies are available."""
        book_to_remove = self._get_book_by_title(book_title)
        if not book_to_remove:
            print(f"[Error] Book '{book_title}' not found.")
            return

        if book_to_remove.available_copies < book_to_remove.total_copies:
            print(f"[Error] Cannot remove book '{book_title}'. {book_to_remove.total_copies - book_to_remove.available_copies} copies are currently borrowed.")
            return
        
        if book_to_remove.reservations:
            print(f"[Error] Cannot remove book '{book_title}'. It has {len(book_to_remove.reservations)} active reservations.")
            return

        del self.books[book_title]
        print(f"[Success] Removed book: {book_title}")
    
    def add_user(self, user_name):
        """Adds a new user to the system."""
        if self._get_user_by_name(user_name):
            print(f"[Error] User '{user_name}' already exists.")
            return

        new_user = User(user_name, self.next_user_id)
        self.users[self.next_user_id] = new_user
        self.next_user_id += 1
        print(f"[Success] Added user: {new_user.name} (ID: {new_user.user_id})")

    def remove_user(self, user_id):
        """Removes a user by ID if they have no loans."""
        try:
            user_id = int(user_id)
        except ValueError:
            print("[Error] User ID must be a number.")
            return

        user_to_remove = self._get_user_by_id(user_id)
        if not user_to_remove:
            print(f"[Error] User with ID {user_id} not found.")
            return

        if user_to_remove.taken_books:
            print(f"[Error] Cannot remove user {user_to_remove.name}. They must return {len(user_to_remove.taken_books)} book(s) first.")
            return

        del self.users[user_id]
        print(f"[Success] Removed user: {user_to_remove.name} (ID: {user_id})")

    # --- TRANSACTION METHODS ---
    def borrow_book(self, user_id, book_title):
        """Issues a book to a user."""
        user = self._get_user_by_id(user_id)
        book = self._get_book_by_title(book_title)

        if not user:
            print(f"[Error] User with ID {user_id} not found.")
            return
        if not book:
            print(f"[Error] Book '{book_title}' not found.")
            return
        if book.available_copies <= 0:
            print(f"[Error] Book '{book_title}' is currently out of copies. Please reserve.")
            return
        if any(loan.book_title == book_title for loan in user.taken_books):
            print(f"[Error] User '{user.name}' already has a copy of this book.")
            return

        # 1. Check reservation queue
        if book.reservations and book.reservations[0] != user.name:
             print(f"[Error] '{book_title}' is reserved by {book.reservations[0]}. You cannot borrow it.")
             return
        
        # 2. Remove user from the reservation queue if they were first
        if book.reservations and book.reservations[0] == user.name:
            book.reservations.pop(0)

        # 3. Create Loan object and update internal state
        loan = Loan(user_id=user.user_id, book_title=book_title)
        user.taken_books.append(loan)
        book.available_copies -= 1
        print(f"[Success] {user.name} borrowed '{book_title}'. Due: {loan.due_date.strftime('%Y-%m-%d')}")

    def return_book(self, user_id, book_title):
        """Handles the return of a book."""
        user = self._get_user_by_id(user_id)
        book = self._get_book_by_title(book_title)

        if not user:
            print(f"[Error] User with ID {user_id} not found.")
            return
        if not book:
            print(f"[Error] Book '{book_title}' not found.")
            return
        
        # 1. Find the loan
        loan_to_remove = next((loan for loan in user.taken_books if loan.book_title == book_title), None)
        
        if not loan_to_remove:
            print(f"[Error] {user.name} does not have '{book_title}' currently borrowed.")
            return

        # 2. Update internal state
        user.taken_books.remove(loan_to_remove)
        book.available_copies += 1
        
        # 3. Notify the next reserved user
        if book.reservations:
            print(f"[Notification] '{book_title}' is now available! Notifying next reservation: {book.reservations[0]}.")

        print(f"[Success] {user.name} returned '{book_title}'.")

    def reserve_book(self, user_id, book_title):
        """Adds a user to the reservation list for a book."""
        user = self._get_user_by_id(user_id)
        book = self._get_book_by_title(book_title)
        
        if not user:
            print(f"[Error] User with ID {user_id} not found.")
            return
        if not book:
            print(f"[Error] Book '{book_title}' not found.")
            return
        
        if book.available_copies > 0:
            print(f"[Error] '{book_title}' is available for immediate borrowing. No need to reserve.")
            return
        
        if user.name in book.reservations:
            print(f"[Error] {user.name} has already reserved this book.")
            return

        book.reservations.append(user.name)
        print(f"[Success] {user.name} reserved '{book_title}'. Queue position: {len(book.reservations)}.")

    # --- REPORTING METHODS ---
    def overdue_books(self):
        """Checks for and prints all overdue loans."""
        overdue_list = []
        for user in self.users.values():
            for loan in user.taken_books:
                if datetime.now() > loan.due_date:
                    overdue_list.append((user, loan))
        
        if not overdue_list:
            print("[Report] No books are currently overdue. Library health is excellent!")
            return

        print("\n--- OVERDUE BOOKS REPORT ---")
        for user, loan in overdue_list:
            print(f"User: {user.name} (ID: {user.user_id})")
            print(f"  Book: '{loan.book_title}' (Due: {loan.due_date.strftime('%Y-%m-%d')})")
        print("----------------------------")
        
        return overdue_list

    def generate_report(self):
        """Prints a general overview of the library's state."""
        total_books = sum(b.total_copies for b in self.books.values())
        available_books = sum(b.available_copies for b in self.books.values())
        total_loans = sum(len(u.taken_books) for u in self.users.values())
        overdue_count = len(self.overdue_books()) # Calls the overdue check

        print("\n--- LIBRARY STATUS REPORT ---")
        print(f"Total Unique Titles: {len(self.books)}")
        print(f"Total Book Copies:   {total_books}")
        print(f"Available Copies:    {available_books} ({available_books / total_books * 100:.1f}% available)")
        print(f"Total Users:         {len(self.users)}")
        print(f"Active Loans:        {total_loans}")
        print(f"Overdue Loans:       {overdue_count}")
        print("----------------------------")
        
        # List Books and Users
        print("\n--- BOOK COLLECTION ---")
        for book in self.books.values():
            print(book)

        print("\n--- ACTIVE USERS ---")
        for user in self.users.values():
            print(user)
            if user.taken_books:
                for loan in user.taken_books:
                    print(loan)
        print("----------------------------")

    # --- PERSISTENCE METHODS ---
    def _get_serializable_data(self):
        """Helper to collect all data into a serializable dictionary."""
        data = {
            "books": [book.to_dict() for book in self.books.values()],
            "users": [user.to_dict() for user in self.users.values()],
            "next_user_id": self.next_user_id
        }
        return data

    def save_to_file(self, filename=FILENAME):
        """Saves the current state of the library to a JSON file."""
        data = self._get_serializable_data()
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"[SUCCESS] Data saved to {filename}")
        except IOError:
            print(f"[ERROR] Could not write to file {filename}.")

    def load_from_file(self, filename=FILENAME):
        """Loads the library state from a JSON file and reconstructs objects."""
        if not os.path.exists(filename):
            print(f"[INFO] File {filename} not found. Starting with empty library.")
            return

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.books = {}
            self.users = {}

            # 1. Reconstruct Books
            for book_data in data.get("books", []):
                self.books[book_data['title']] = Book(**book_data)

            # 2. Reconstruct Users (handles nested Loan objects)
            for user_data in data.get("users", []):
                loan_data = user_data.pop('taken_books')
                user_obj = User(**user_data)
                
                for loan_dict in loan_data:
                    loan_obj = Loan(**loan_dict)
                    user_obj.taken_books.append(loan_obj)

                self.users[user_obj.user_id] = user_obj

            # 3. Restore next ID
            self.next_user_id = data.get("next_user_id", 1)
            
            print(f"[SUCCESS] Data loaded successfully from {filename}.")
            print(f"Loaded {len(self.books)} books and {len(self.users)} users.")

        except json.JSONDecodeError:
            print(f"[ERROR] File {filename} is corrupted (Invalid JSON format).")
        except IOError:
            print(f"[ERROR] Could not read file {filename}.")


# ===============================================
# MAIN PROGRAM LOOP
# ===============================================

def display_menu():
    """Prints the user menu."""
    print("\n--- Library Management System Menu ---")
    print("1: Add Book")
    print("2: Remove Book")
    print("3: Add User")
    print("4: Remove User")
    print("5: Borrow Book")
    print("6: Return Book")
    print("7: Reserve Book")
    print("8: Show Reports (General/Overdue)")
    print("9: Save Data")
    print("10: Load Data")
    print("0: Exit")
    return input("Enter your choice: ")

def get_input(prompt, cast_to=str):
    """Helper for user input with optional type casting."""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                return None
            return cast_to(user_input)
        except ValueError:
            print(f"[Error] Invalid input. Must be a {cast_to.__name__}.")

def main():
    library = Library()
    library.load_from_file() # Auto-load on startup

    while True:
        choice = display_menu()

        if choice == '1':
            title = get_input("Book Title: ")
            author = get_input("Author: ")
            copies = get_input("Number of Copies: ", int)
            if title and author and copies is not None:
                library.add_book(title, author, copies)
        
        elif choice == '2':
            title = get_input("Book Title to remove: ")
            if title:
                library.remove_book(title)

        elif choice == '3':
            name = get_input("User Name: ")
            if name:
                library.add_user(name)

        elif choice == '4':
            user_id = get_input("User ID to remove: ", int)
            if user_id is not None:
                library.remove_user(user_id)
        
        elif choice == '5':
            user_id = get_input("User ID (borrower): ", int)
            title = get_input("Book Title to borrow: ")
            if user_id is not None and title:
                library.borrow_book(user_id, title)

        elif choice == '6':
            user_id = get_input("User ID (returner): ", int)
            title = get_input("Book Title to return: ")
            if user_id is not None and title:
                library.return_book(user_id, title)
                
        elif choice == '7':
            user_id = get_input("User ID (reserver): ", int)
            title = get_input("Book Title to reserve: ")
            if user_id is not None and title:
                library.reserve_book(user_id, title)

        elif choice == '8':
            library.generate_report()
            
        elif choice == '9':
            library.save_to_file()
            
        elif choice == '10':
            library.load_from_file()

        elif choice == '0':
            print("Saving data before exit...")
            library.save_to_file()
            print("Exiting Library Management System. Goodbye!")
            break
        
        else:
            print("[Error] Invalid choice. Please select a number from the menu.")

if __name__ == "__main__":
    main()

import json
from datetime import datetime, timedelta

# ===============================================
# CORE ENTITY CLASSES
# ===============================================

class Book:
    """Stores book details, availability, and reservation list."""
    def __init__(self, title, author, total_copies):
        self.title = title
        self.author = author
        self.total_copies = total_copies
        self.available_copies = total_copies
        self.reservations = []  # List of User names who reserved the book
    
    # OOP: The __str__ method allows the object to be printed cleanly.
    def __str__(self):
        return f"Book(Title: '{self.title}', Author: {self.author}, Available: {self.available_copies}/{self.total_copies})"

class User:
    """Stores user details and tracks the books they currently hold."""
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id
        self.taken_books = []  # List of Loan objects
    
    def __str__(self):
        return f"User(Name: {self.name}, ID: {self.user_id}, Loans: {len(self.taken_books)})"

class Loan:
    """Links a specific User and a Book; tracks the due date."""
    def __init__(self, user_id, book_title):
        self.user_id = user_id
        self.book_title = book_title
        self.issue_date = datetime.now()
        # Set a fixed return period (e.g., 14 days)
        self.due_date = self.issue_date + timedelta(days=14)
    
    def __str__(self):
        return (f"Loan(User ID: {self.user_id}, Book: '{self.book_title}', "
                f"Due: {self.due_date.strftime('%Y-%m-%d')})")


# ===============================================
# MANAGER CLASS (Encapsulation and Logic)
# ===============================================

class Library:
    """Manages the collection of all Books, Users, and Loans."""
    def __init__(self):
        # OOP: These instance variables encapsulate all the system's data.
        self.books = {}     # Key: book title, Value: Book object
        self.users = {}     # Key: user ID, Value: User object
        self.next_user_id = 1
        
    def add_book(self, book):
        """Method to add a book (demonstrates simple OOP method)."""
        if book.title in self.books:
            print(f"[Error] Book '{book.title}' already exists.")
            return
        self.books[book.title] = book
        print(f"[Success] Added book: {book.title}")

    # The rest of the methods (borrow_book, return_book, save_to_file, etc.)
    # will be implemented here, defining the full system logic.


# ===============================================
# MAIN EXECUTION BLOCK (Demonstration)
# ===============================================

if __name__ == "__main__":
    library_manager = Library()

    # 1. Demonstrate object creation
    book1 = Book("The Python Bible", "Guido", 3)
    user1 = User("Alice", library_manager.next_user_id)
    library_manager.next_user_id += 1
    
    # 2. Demonstrate simple encapsulation via a manager method
    library_manager.add_book(book1)
    
    print("\n--- Objects Created ---")
    print(book1)
    print(user1)

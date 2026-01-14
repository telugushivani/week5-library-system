import json
from datetime import datetime, timedelta

# ---------------- BOOK CLASS ----------------
class Book:
    def __init__(self, title, author, isbn, year):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.available = True
        self.borrowed_by = None
        self.due_date = None

    def check_out(self, member_id, days=14):
        if not self.available:
            return False, "Book already borrowed"

        self.available = False
        self.borrowed_by = member_id
        self.due_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        return True, f"Book borrowed. Due date: {self.due_date}"

    def return_book(self):
        self.available = True
        self.borrowed_by = None
        self.due_date = None

    def is_overdue(self):
        if self.due_date:
            return datetime.now() > datetime.strptime(self.due_date, "%Y-%m-%d")
        return False

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        book = cls(data["title"], data["author"], data["isbn"], data["year"])
        book.available = data["available"]
        book.borrowed_by = data["borrowed_by"]
        book.due_date = data["due_date"]
        return book

    def __str__(self):
        status = "Available" if self.available else f"Borrowed (Due {self.due_date})"
        return f"{self.title} | {self.author} | {self.isbn} | {status}"


# ---------------- MEMBER CLASS ----------------
class Member:
    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id
        self.borrowed_books = []

    def borrow_book(self, isbn):
        if len(self.borrowed_books) >= 5:
            return False, "Borrow limit reached"
        self.borrowed_books.append(isbn)
        return True, "Book added to member account"

    def return_book(self, isbn):
        if isbn in self.borrowed_books:
            self.borrowed_books.remove(isbn)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        m = cls(data["name"], data["member_id"])
        m.borrowed_books = data["borrowed_books"]
        return m


# ---------------- LIBRARY CLASS ----------------
class Library:
    def __init__(self):
        self.books = {}
        self.members = {}

    # BOOK METHODS
    def add_book(self, book):
        self.books[book.isbn] = book

    def find_book(self, keyword):
        results = []
        for book in self.books.values():
            if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower() or keyword == book.isbn:
                results.append(book)
        return results

    # MEMBER METHODS
    def register_member(self, member):
        self.members[member.member_id] = member

    # BORROW
    def borrow_book(self, isbn, member_id):
        if isbn not in self.books:
            return "Book not found"

        if member_id not in self.members:
            return "Member not found"

        book = self.books[isbn]
        member = self.members[member_id]

        ok, msg = book.check_out(member_id)
        if not ok:
            return msg

        member.borrow_book(isbn)
        return msg

    # RETURN
    def return_book(self, isbn, member_id):
        book = self.books[isbn]
        member = self.members[member_id]

        overdue = book.is_overdue()
        book.return_book()
        member.return_book(isbn)

        if overdue:
            return "Book returned (Overdue)"
        return "Book returned successfully"

    # STATS
    def statistics(self):
        total = len(self.books)
        available = sum(1 for b in self.books.values() if b.available)
        return total, available

    # FILE SAVE
    def save_data(self):
        with open("books.json", "w") as f:
            json.dump({k: v.to_dict() for k, v in self.books.items()}, f)

        with open("members.json", "w") as f:
            json.dump({k: v.to_dict() for k, v in self.members.items()}, f)

    # FILE LOAD
    def load_data(self):
        try:
            with open("books.json") as f:
                data = json.load(f)
                for k, v in data.items():
                    self.books[k] = Book.from_dict(v)
        except:
            pass

        try:
            with open("members.json") as f:
                data = json.load(f)
                for k, v in data.items():
                    self.members[k] = Member.from_dict(v)
        except:
            pass


# ---------------- MENU SYSTEM ----------------
def menu():
    print("\n--- LIBRARY MENU ---")
    print("1. Add Book")
    print("2. Register Member")
    print("3. Borrow Book")
    print("4. Return Book")
    print("5. Search Book")
    print("6. Statistics")
    print("7. Save & Exit")


# ---------------- MAIN PROGRAM ----------------
lib = Library()
lib.load_data()

while True:
    menu()
    choice = input("Enter choice: ")

    if choice == "1":
        t = input("Title: ")
        a = input("Author: ")
        i = input("ISBN: ")
        y = input("Year: ")
        lib.add_book(Book(t, a, i, y))
        print("Book added")

    elif choice == "2":
        n = input("Member name: ")
        mid = input("Member ID: ")
        lib.register_member(Member(n, mid))
        print("Member registered")

    elif choice == "3":
        i = input("ISBN: ")
        mid = input("Member ID: ")
        print(lib.borrow_book(i, mid))

    elif choice == "4":
        i = input("ISBN: ")
        mid = input("Member ID: ")
        print(lib.return_book(i, mid))

    elif choice == "5":
        k = input("Search keyword: ")
        results = lib.find_book(k)
        for b in results:
            print(b)

    elif choice == "6":
        total, avail = lib.statistics()
        print(f"Total Books: {total}")
        print(f"Available Books: {avail}")

    elif choice == "7":
        lib.save_data()
        print("Data saved. Goodbye!")
        break

    else:
        print("Invalid choice")


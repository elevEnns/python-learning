class Book:
    """记录书籍信息"""
    def __init__(self, title, author, isbn, available = True):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = available

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) {self.available}"

class User:
    """记录用户信息"""
    def __init__(self, name, student_id, borrowed_books = None):
        if borrowed_books is None:
            borrowed_books = []
        self.borrowed_books = borrowed_books
        self.name = name
        self.student_id = student_id


    def __str__(self):
        return f"{self.name} (ID: {self.student_id}) Borrowed books: {self.borrowed_books}"
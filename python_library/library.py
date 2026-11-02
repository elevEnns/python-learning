import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Book:
    """记录书籍信息"""
    def __init__(self, title, author, isbn, available=True):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = available

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) {self.available}"

class User:
    """记录用户信息"""
    def __init__(self, name, student_id, borrowed_books=None):
        if borrowed_books is None:
            borrowed_books = []
        self.borrowed_books = borrowed_books
        self.name = name
        self.student_id = student_id


    def __str__(self):
        return f"{self.name} (ID: {self.student_id}) Borrowed books: {self.borrowed_books}"

class BookNotFoundError(Exception):
    """书不存在"""
    pass

class UserNotFoundError(Exception):
    """用户不存在"""
    pass

class BookNotAvailableError(Exception):
    """书已被借出"""
    pass

class BookNotBorrowedError(Exception):
    """用户没有借这本书"""
    pass

class Library:
    """图书管理系统：管理所有书和用户"""
    def __init__(self):
        self.book_list = []     # 存 Book 对象
        self.user_list = []     # 存 User 对象


    # —— 书的增删查改 ——
    def add_book(self, book):
        """把 book 加进 book_list"""
        self.book_list.append(book)
        logging.info(f"Book added: {book.title}")

    def list_books(self):
        """打印所有书"""
        for book in self.book_list:
            print(book)

    def find_book(self, isbn):
        """按 isbn 找书：找到返回 Book 对象，找不到返回 None"""
        for book in self.book_list:
            if book.isbn == isbn:
                return book
        return None

    def delete_book(self, isbn):
        """按 isbn 删书：找到就删，找不到打印提示"""
        book = self.find_book(isbn)
        if book is None:
            logging.warning("Book not found")
            return
        self.book_list.remove(book)
        logging.info(f"Book deleted: {book.title}")

    def update_book(self, isbn, **kwargs):
        """按 isbn 改书的信息（kwargs 里是要改的字段，如 title="新名字"）"""
        book = self.find_book(isbn)
        if book is None:
            logging.warning("Book not found")
            return
        allowed_fields = {"title", "author", "isbn", "available"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(book, key, value)


    # —— 用户管理 ——
    def add_user(self, user):
        """把 user 加进 user_list"""
        self.user_list.append(user)
        logging.info(f"User added: {user.name}")

    def find_user(self, student_id):
        """按 student_id 找用户：找到返回 User，找不到返回 None"""
        for user in self.user_list:
            if user.student_id == student_id:
                return user
        return None

    # —— 借书还书 ——
    def borrow_book(self, student_id, isbn):
        """借书：找到书和用户，书标记借出，加进用户 borrowed_books"""
        user = self.find_user(student_id)
        if user is None:
            raise UserNotFoundError("User not found")

        book = self.find_book(isbn)
        if book is None:
            raise BookNotFoundError("Book not found")

        if not book.available:
            raise BookNotAvailableError("Book not available")

        book.available = False
        user.borrowed_books.append(book)
        logging.info(f"{book.title} borrowed by {user.name}")

    def return_book(self, student_id, isbn):
        """还书：找到书和用户，书标记在库，从用户 borrowed_books 移除"""
        book = self.find_book(isbn)
        if book is None:
            raise BookNotFoundError("Book not found")

        user = self.find_user(student_id)
        if user is None:
            raise UserNotFoundError("User not found")

        if book not in user.borrowed_books:
            raise BookNotBorrowedError("This book was not borrowed by this user")

        book.available = True
        user.borrowed_books.remove(book)
        logging.info(f"{book.title} returned by {user.name}")

a = Library()
b = Book("Python for Beginners", "Alison Bock", "1234567890")
c = Book("1","2","123")
a.add_book(b)

u = User("张三", "2024001")
a.add_user(u)

a.list_books()                    # available=True

a.borrow_book("2024001", "1234567890")
a.list_books()                    # available=False

a.return_book("2024001", "1234567890")   # ← 补上这行
a.list_books()                    # available=True


# 再次借书然后测试书已借出的异常

try:
    a.return_book("2024001", "1234567890")
except BookNotBorrowedError as e:
    logging.warning(e)
except UserNotFoundError as e:
    logging.warning(e)
except BookNotAvailableError as e:
    logging.warning(e)
except UserNotFoundError as e:
    logging.warning(e)

if __name__ == "__main__":
    a = Library()
    b = Book("Python for Beginners", "Alison Bock", "1234567890")
    a.add_book(b)



import pytest
from library import (Library, Book, User,
                     BookNotFoundError, UserNotFoundError,
                     BookNotAvailableError, BookNotBorrowedError)


def test_add_book():
    lib = Library()
    book = Book("Python", "Author", "111")
    lib.add_book(book)
    assert len(lib.book_list) == 1
    assert lib.book_list[0].title == "Python"


def test_find_book():
    lib = Library()
    book = Book("Python", "Author", "111")
    lib.add_book(book)
    assert lib.find_book("111") == book
    assert lib.find_book("999") is None


def test_borrow_book_not_found():
    lib = Library()
    user = User("张三", "2024001")
    lib.add_user(user)              # ← 先加用户，让 find_user 能通过
    with pytest.raises(BookNotFoundError):
        lib.borrow_book("2024001", "999")   # 现在才会走到"书不存在"

def test_borrow_book_not_available():
    lib = Library()
    book = Book("Python", "Author", "111")
    user = User("张三", "2024001")
    lib.add_user(user)
    lib.add_book(book)
    lib.borrow_book("2024001", "111")
    with pytest.raises(BookNotAvailableError):
        lib.borrow_book("2024001", "111")

def test_return_book_not_borrowed():
    lib = Library()
    book = Book("Python", "Author", "111")
    user = User("张三", "2024001")
    lib.add_user(user)
    lib.add_book(book)
    with pytest.raises(BookNotBorrowedError):
        lib.return_book("2024001", "111")

def test_borrow_book_success():
    lib = Library()
    book = Book("Python", "Author", "111")
    user = User("张三", "2024001")
    lib.add_user(user)
    lib.add_book(book)
    lib.borrow_book("2024001", "111")
    assert book.available == False
    assert book in user.borrowed_books

def test_return_book_success():
    lib = Library()
    book = Book("Python", "Author", "111")
    user = User("张三", "2024001")
    lib.add_user(user)
    lib.add_book(book)
    lib.borrow_book("2024001", "111")
    lib.return_book("2024001", "111")
    assert book.available == True
    assert book not in user.borrowed_books

def test_delete_book():
    lib = Library()
    book = Book("Python", "Author", "111")
    user = User("张三", "2024001")
    lib.add_user(user)
    lib.add_book(book)
    lib.delete_book("111")
    assert (len(lib.book_list) == 0)

def test_update_book():
    lib = Library()
    book = Book("Python", "Author", "111")
    lib.add_book(book)
    lib.update_book("111", title='java')
    assert book.title == "java"

def test_add_user_find_user():
    lib = Library()
    user = User("张三", "2024001")
    lib.add_user(user)
    assert lib.find_user("2024001") == user

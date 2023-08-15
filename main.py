from pathlib import Path
import requests


def get_books(number_of_books, path_to_save='books'):
    '''Downloads firs N books (number_of_books) from tululu.org
       and saves them specified path'''

    Path(path_to_save).mkdir(parents=True, exist_ok=True)
    for book_id in range(1, number_of_books + 1):
        book_url = f'https://tululu.org/txt.php?id={book_id}'
        book_response = requests.get(book_url)
        book_response.raise_for_status()

        with open(Path(path_to_save, f'id{book_id}.txt'), 'wb') as book:
            book.write(book_response.content)


def main():
    get_books(10)


if __name__ == '__main__':
    main()

import argparse
from time import sleep
import requests
from requests.exceptions import HTTPError
from parser_helpers import (check_for_redirect, download_txt,
                            downlaod_image, parse_book_page)


def main():
    '''Main function'''
    books_parser = argparse.ArgumentParser(
        description='''Program downloads books from https://tululu.org/ by
                       passed book page ids. To load multiple books, enter
                       start_id and end_id. Both identifiers will be included
                       in the range. By default start_id = 1 end_id = 10.
                       To load only one book, pass the same id for start_id and
                       end_id.'''
    )
    books_parser.add_argument('-s', '--start_id',
                              default=1,
                              type=int,
                              help='start value of the range')
    books_parser.add_argument('-e', '--end_id',
                              default=10,
                              type=int,
                              help='end value of the range')
    args = books_parser.parse_args()
    main_page = 'https://tululu.org/'

    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f'{main_page }b{book_id}/'
        conn = True
        while conn:
            try:
                book_response = requests.get(book_url, allow_redirects=False)
                book_response.raise_for_status()
                check_for_redirect(book_response, file=f'book_id {book_id}')
                book_response_content = book_response.content
                parsed_book_page = parse_book_page(book_response_content,
                                                   book_url)
                book_title = parsed_book_page.get('title')
                download_txt(parsed_book_page.get('txt url'),
                             filename=f'{book_id} {book_title}')
                downlaod_image(parsed_book_page.get('image url'))
                conn = False
            except HTTPError as http_err:
                print(http_err, end='\n\n')
                conn = False
            except requests.exceptions.ConnectionError as conn_err:
                print(conn_err, end='\n\n')
                sleep(180)
            else:
                print(f"Название: {book_title}",
                      f"Автор: {parsed_book_page.get('author')}",
                      f"Жанр: {'; '.join(parsed_book_page.get('genres'))}",
                      sep='\n', end='\n\n')


if __name__ == '__main__':
    main()

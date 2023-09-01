from pathlib import Path
from urllib.parse import urljoin
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename
import argparse


def is_redirected(response) -> bool:
    '''Checks are there redirect in history of ressponse to the main page'''
    return response.url == 'https://tululu.org/'


def get_book_name_and_author(book_url: str) -> tuple:
    '''Parses book title and book author by book url'''
    book_response = requests.get(book_url)
    book_response.raise_for_status()
    soup = BeautifulSoup(book_response.content, 'lxml')
    book_title_author = soup.find(id='content').find('h1').text.split('::')
    return book_title_author[0].strip(), book_title_author[1].strip()


def download_txt(url: str, filename: str, folder='books/') -> Path:
    """Loads txt file
       Args:
        url - link to the text file.
        filename - The name of the file to save with.
        folder - Folder to save to.
       Returns:
        Path to the file where the text is saved.
    """
    sanitized_folder = Path(sanitize_filepath(folder))
    sanitized_filename = sanitize_filename(filename)
    sanitized_folder.mkdir(parents=True, exist_ok=True)
    full_path = Path(sanitized_folder, f'{sanitized_filename}.txt')
    book_response = requests.get(url)
    book_response.raise_for_status()
    with open(full_path, 'wb') as book:
        book.write(book_response.content)
    return full_path


def get_url_of_book_text(book_html: bytes,
                         book_title: str,
                         book_url: str) -> str:
    '''Returns url of text file from book url'''
    soup = BeautifulSoup(book_html, 'lxml')
    relative_link = soup.find(id='content').find(
                        'a', title=f'{book_title} - скачать книгу txt')['href']
    return urljoin(book_url, relative_link)


def downlaod_image(book_html: bytes, folder='images/') -> Path:
    """Loads image file
       Args:
        book_html - Html page of the book.
        folder - Folder to save to.
       Returns:
        Path to the file where the image is saved.
    """
    soup = BeautifulSoup(book_html, 'lxml')
    image_relative_path = soup.find(class_='bookimage').find('img').get('src')
    image_url = urljoin('https://tululu.org/', image_relative_path)
    image_name = image_relative_path.split('/')[-1]
    sanitized_folder = Path(sanitize_filepath(folder))
    sanitized_folder.mkdir(parents=True, exist_ok=True)
    path_to_save = Path(sanitized_folder, image_name)
    with open(path_to_save, 'wb') as image:
        image.write(requests.get(image_url).content)
    return path_to_save


def parse_book_page(book_html: bytes) -> dict:
    '''Returns dict with parsed book title, book genres and book comments
    '''
    soup = BeautifulSoup(book_html, 'lxml')
    title_and_author = soup.find(id='content').find('h1').text.split('::')
    title, author = (el.strip() for el in title_and_author)
    genres = [tag.text for tag in soup.find(id='content')  \
                .find('span', class_='d_book').find_all('a')]
    comment_tags = soup.find(id="content").find_all(class_='black')
    comments = [tag.text for tag in comment_tags]

    return {
        'book title': title,
        'book author': author,
        'book genres': genres,
        'book comments': comments,
    }


def main():
    '''Main function'''
    books_parser = argparse.ArgumentParser(
        description='''Program downloads books from https://tululu.org/
                       by passed ids of book pages.
                       Enter start_id and end_id to download several books.
                       Both ids would be included.'''
    )
    books_parser.add_argument('-s', '--start_id', default=1, type=int)
    books_parser.add_argument('-e', '--end_id', default=10, type=int)
    args = books_parser.parse_args()

    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f'https://tululu.org/b{book_id}'
        book_response = requests.get(book_url)
        conn = True
        while conn:
            try:
                book_response.raise_for_status()
                if is_redirected(book_response):
                    raise HTTPError(f'Data for book id {book_id} not found.')
                book_response_content = book_response.content
                parsed_book_page = parse_book_page(book_response_content)
                book_title = parsed_book_page['book title']
                book_txt_url = get_url_of_book_text(book_response_content,
                                                    book_title,
                                                    book_url)
                if not book_txt_url:
                    print('Data for book id', {book_id}, f'"{book_title}"',
                          'not found.', end='\n\n')
                    conn = False
                    continue
                download_txt(book_txt_url, filename=f'{book_id} {book_title}')
                downlaod_image(book_response_content)
                conn = False
            except HTTPError as http_err:
                print(http_err, end='\n\n')
                conn = False
            except requests.exceptions.ConnectionError as conn_err:
                print(conn_err, end='\n\n')
            else:
                print(f"Название: {book_title}",
                      f"Автор: {parsed_book_page['book author']}",
                      f"Жанр: {'; '.join(parsed_book_page['book genres'])}",
                      sep='\n', end='\n\n')


if __name__ == '__main__':
    main()

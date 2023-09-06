from pathlib import Path
import argparse
from urllib.parse import urljoin
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename


def check_for_redirect(response: requests.models.Response, file, raise_err=True):
    '''Checks for redirects and, if so, raises an HTTPError'''
    if response.is_redirect:
        if raise_err:
            raise HTTPError(f'Data for {file} not found.')
        print(f'Data for {file} not found.')


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
    book_response = requests.get(url, allow_redirects=False)
    check_for_redirect(book_response, file=filename)
    book_response.raise_for_status()
    with open(full_path, 'wb') as book:
        book.write(book_response.content)
    return full_path


def downlaod_image(image_url: str, folder='images/') -> Path:
    """Loads image file
       Args:
        image_url - url of book image.
        folder - folder to save to.
       Returns:
        Path to the file where the image is saved.
    """
    image_name = image_url.split('/')[-1]
    sanitized_folder = Path(sanitize_filepath(folder))
    sanitized_folder.mkdir(parents=True, exist_ok=True)
    path_to_save = Path(sanitized_folder, image_name)
    with open(path_to_save, 'wb') as image:
        image_response =requests.get(image_url, allow_redirects=False)
        image_response.raise_for_status()
        check_for_redirect(image_response,
                           file=f'image {image_name}',
                           raise_err=False)
        image.write(image_response.content)
    return path_to_save


def parse_book_page(book_html: bytes, book_url: str) -> dict:
    '''Returns dict with parsed:
        - title - book title (str)
        - genres - book genres (list)
        - comments - book comments (list)
        - txt url - url for downloading book in txt format (str)
        - image url - url of book image
    '''
    soup = BeautifulSoup(book_html, 'lxml')
    title_and_author = soup.find(id='content').find('h1').text.split('::')
    title, author = (el.strip() for el in title_and_author)
    genres = [tag.text for tag in soup.find(id='content')  \
                .find('span', class_='d_book').find_all('a')]
    comment_tags = soup.find(id="content").find_all(class_='black')
    comments = [tag.text for tag in comment_tags]

    book_txt_tag = soup.find(id='content').find(
                    'a', title=f'{title} - скачать книгу txt')
    if book_txt_tag is None:
        raise HTTPError(f'Data for book "{title}" not found.')
    txt_relative_link = book_txt_tag["href"]
    txt_url = urljoin(book_url, txt_relative_link)

    image_relative_path = soup.find(class_='bookimage').find('img').get('src')
    image_url = urljoin(book_url, image_relative_path)

    return {
        'title': title,
        'author': author,
        'genres': genres,
        'comments': comments,
        'txt url': txt_url,
        'image url': image_url,
    }


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
            else:
                print(f"Название: {book_title}",
                      f"Автор: {parsed_book_page.get('author')}",
                      f"Жанр: {'; '.join(parsed_book_page.get('genres'))}",
                      sep='\n', end='\n\n')


if __name__ == '__main__':
    main()

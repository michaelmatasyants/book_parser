from pathlib import Path
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename
from urllib.parse import urlparse, urljoin


def check_for_redirect(url: str, text=''):
    '''Checks are there redirect in history of ressponse'''
    response = requests.get(url)
    response.raise_for_status()
    if response.url == 'https://tululu.org/':
        raise HTTPError(f'Data for {text} not found.')


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


def get_url_of_book_text(book_url: str) -> str:
    response = requests.get(book_url)
    soup = BeautifulSoup(response.content, 'lxml')
    all_tags_a = soup.find(class_='d_book').find_all('a')
    for tag in all_tags_a:
        if 'скачать txt' in tag:
            return urljoin('https://tululu.org/', tag.get("href"))


def downlaod_img(book_url: str, folder='images/') -> Path:
    """Loads image file
       Args:
        book_url - link to the image file.
        folder - Folder to save to.
       Returns:
        Path to the file where the image is saved.
    """
    soup = BeautifulSoup(requests.get(book_url).content, 'lxml')
    image_relative_path = soup.find(class_='bookimage').find('img').get('src')
    image_url = urljoin('https://tululu.org/', image_relative_path)
    image_name = image_relative_path.split('/')[-1]
    sanitized_folder = Path(sanitize_filepath(folder))
    sanitized_folder.mkdir(parents=True, exist_ok=True)
    path_to_save = Path(sanitized_folder, image_name)
    with open(path_to_save, 'wb') as image:
        image.write(requests.get(image_url).content)
    return path_to_save


def main():
    for book_id in range(1, 11):
        book_url = f'https://tululu.org/b{book_id}'
        try:
            check_for_redirect(book_url, text=f'book id {book_id}')
        except HTTPError as err:
            print(err)
            continue
        book_name = f'{book_id} {get_book_name_and_author(book_url)[0]}'
        book_txt_url = get_url_of_book_text(book_url)
        if book_txt_url:
            download_txt(book_txt_url, book_name)
        else:
            print(f'Data for "{book_name}" not found.')
        downlaod_img(book_url)


if __name__ == '__main__':
    main()

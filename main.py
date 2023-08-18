from pathlib import Path
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename


def check_for_redirect(response: requests.models.Response, text=''):
    '''Checks are there redirect in history of ressponse'''
    if response.url == 'https://tululu.org/':
        raise HTTPError(f'Data for {text} not found')


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
    book_response = requests.get(url)
    book_response.raise_for_status()
    full_path = Path(sanitized_folder, f'{sanitized_filename}.txt')
    try:
        check_for_redirect(book_response, text='id book')
    except HTTPError as err:
        print(err)
    with open(full_path, 'wb') as book:
        book.write(book_response.content)
    return full_path


def main():
    download_txt('http://tululu.org/txt.php?id=1', 'filename')


if __name__ == '__main__':
    main()

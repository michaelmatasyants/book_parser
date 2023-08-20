# Book parser from tululu.org

This program helps you download and save books from tululu.org in txt format. It also saves the book cover, title, author, genres this book belongs to and other user's comments about the book.
You can download several books at once by passing the book id range.

## How to run

1. To run the parser you should already have Python 3 and pip (package-management system) installed.

2. Download the code.

3. Create a virtual environment with its own independent set of packages using [virtualenv/venv](https://docs.python.org/3/library/venv.html). It'll help you to isolate the project from the packages located in the base environment.

4. Install all the packages used in this project, in your virtual environment which you've created on the step 2. Use the `requirements.txt` file to install dependencies: `pip install -r requirements.txt`

5. Then to load books with id 20 to id 30 inclusive, run `python3 main.py -s 20 -e 30` where numbers are the range of book id's

## Arguments

start_id, end_id - are used to specify the range of books to be downloaded.<br>
The book id is used to generate book links on the tululu site, from where links to the text file of the book itself are parsed, as well as other information.


## Project Purpose

The code is written for educational purposes
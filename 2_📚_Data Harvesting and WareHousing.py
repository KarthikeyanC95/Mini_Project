import pymysql
import requests
import streamlit as st
from mysql.connector import Error
import pandas as pd


# Google Books API Key (Replace with your actual API key)
API_KEY = 'AIzaSyBa_59ZupTnQEOzwpiXh2w9sQuayhveCcY'

# Base URL for Google Books API
BASE_URL = "https://www.googleapis.com/books/v1/volumes"

def fetch_books(query, max_results=40, start_index=0):
    # Prepare the request URL with parameters
    url = f"{BASE_URL}?q={query}&maxResults={max_results}&startIndex={start_index}&key={API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    # If the response has items, process the data
    if 'items' in data:
        books = []
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            sale_info = item.get('saleInfo', {})
            industry_Identifiers = volume_info.get('industryIdentifiers', [])
            book_data = {
                    'book_id' : item.get('id', 'N/A'),  # Book ID
                    'search_key' : query,  # Search key (selfLink is unique)
                    'book_title' : volume_info.get('title', 'N/A'),  # Book title
                    'book_subtitle' : volume_info.get('subtitle', 'N/A'),  # Book subtitle
                    'book_authors' : ', '.join(volume_info.get('authors', ['N/A'])),  # Authors
                    'book_description' : volume_info.get('description', 'No description available.'),  # Description
            
                    # Concatenate all types in industryIdentifiers directly
                    'industryIdentifiers' : ''.join([identifier.get('type', 'N/A') for identifier in industry_Identifiers]),  # Concatenate types
            
                    'text_readingModes' : volume_info.get('readingModes', {}).get('text', 'False'),  # Text reading mode
                    'image_readingModes' : volume_info.get('readingModes', {}).get('image', 'False') , # Image reading mode
                    'pageCount' : volume_info.get('pageCount', '0'),  # Page count
                    'categories' : ', '.join(volume_info.get('categories', ['N/A'])),  # Categories
                    'language' : volume_info.get('language', 'N/A'),  # Language
                    'imageLinks' : volume_info.get('imageLinks', {}).get('thumbnail', 'No thumbnail available.'),  # Image links
                    'ratingsCount' : volume_info.get('ratingsCount', '0'),  # Ratings count
                    'averageRating' : volume_info.get('averageRating', '0'),  # Average rating
                    'country' : volume_info.get('country', 'N/A'),  # Country (publication)
                    'saleability' : sale_info.get('saleability', 'N/A'),  # Saleability
                    'isEbook' : sale_info.get('isEbook', 'False'),  # Is ebook
                    'amount_listPrice' : sale_info.get('listPrice', {}).get('amount', '0.0'),  # Amount listPrice
                    'currencyCode_listPrice' : sale_info.get('listPrice', {}).get('currencyCode', 'N/A'),  # Currency code listPrice
                    'amount_retailPrice' : sale_info.get('retailPrice', {}).get('amount', '0.0'),  # Amount retailPrice
                    'currencyCode_retailPrice' : sale_info.get('retailPrice', {}).get('currencyCode', 'N/A'),  # Currency code retailPrice
                    'buyLink' : volume_info.get('infoLink', 'NA'),  # Buy link
                    'year' : volume_info.get('publishedDate', '0000')[:4],  # Year (from publishedDate)
                    'publisher' : volume_info.get('publisher', 'Not available'),  # Publisher
            }
            books.append(book_data)
        
        return books
    else:
        return []

def fetch_books_paginated(query, max_results_per_page=40, total_results=1000):
    all_books = []
    start_index = 0
    while start_index < total_results:
        books = fetch_books(query, max_results=max_results_per_page, start_index=start_index)
        if books:
            all_books.extend(books)
        start_index += max_results_per_page
        if len(books) < max_results_per_page:  # No more results available
            break
    return all_books


def display_books(books):
    if books:
        # Convert to a DataFrame for easier display
        df = pd.DataFrame(books)
        # Ensure 'ratingsCount' is numeric and handle any invalid values
        df['ratingsCount'] = pd.to_numeric(df['ratingsCount'], errors='coerce').fillna(0).astype(int)
        df['averageRating'] = pd.to_numeric(df['averageRating'], errors='coerce').fillna(0.0).astype(float)
        df['amount_listPrice'] = pd.to_numeric(df['amount_listPrice'], errors='coerce').fillna(0.0).astype(float)
        df['amount_retailPrice'] = pd.to_numeric(df['amount_retailPrice'], errors='coerce').fillna(0.0).astype(float)
        st.write(df)
    else:
        st.write("No books found.")
    

def insert_books_into_mysql(books):
    # Establish connection to MySQL
    connection = pymysql.connect(
        host="localhost",        # Your MySQL host
        user="root",    # Your MySQL username
        password="mysql",
        database="Book_details",
        cursorclass=pymysql.cursors.DictCursor
    )

    if connection:
        cursor = connection.cursor()
        for book in books:
            try:
                # Safely get values using get() to handle missing keys
                ratingsCount = book.get('ratingsCount', 0) if isinstance(book.get('ratingsCount', 0), int) else 0
                averageRating = book.get('averageRating', 0.0) if isinstance(book.get('averageRating', 0.0), (int, float)) else 0.0
                amount_listPrice = book.get('amount_listPrice', 0.0) if isinstance(book.get('amount_listPrice', 0.0), (int, float)) else 0.0
                amount_retailPrice = book.get('amount_retailPrice', 0.0) if isinstance(book.get('amount_retailPrice', 0.0), (int, float)) else 0.0
                currencycode_listprice = book.get('currencyCode_listPrice', 'N/A')
                currencycode_retailprice = book.get('currencycode_retailprice', 'N/A')  # Use get() for this key
                buyLink = book.get('buyLink', 'N/A')
                year = book.get('year', '0000')
                publisher = book.get('publisher', 'Not available')

                # Prepare data tuple
                data_tuple = (
                    book.get('book_id', 'N/A'), book.get('search_key', 'N/A'), book.get('book_title', 'N/A'),
                    book.get('book_subtitle', 'N/A'), book.get('book_authors', 'N/A'), book.get('book_description', 'No description available'),
                    book.get('industryIdentifiers', 'N/A'), book.get('text_readingModes', 'False'),
                    book.get('image_readingModes', 'False'), book.get('pageCount', 0), book.get('categories', 'N/A'),
                    book.get('language', 'N/A'), book.get('imageLinks', 'No thumbnail available'), ratingsCount,
                    averageRating, book.get('country', 'N/A'), book.get('saleability', 'N/A'), book.get('isEbook', 'False'),
                    amount_listPrice, currencycode_listprice, amount_retailPrice, currencycode_retailprice, buyLink, year, publisher
                )

                insert_query = """
                INSERT INTO Book_details.books_details (
                    book_id, search_key, book_title, book_subtitle, book_authors, book_description, industryIdentifiers, text_readingModes, image_readingModes, pageCount, 
                    categories, language, imageLinks, ratingsCount, averageRating, country, saleability, isEbook, amount_listPrice, currencycode_listprice, amount_retailPrice, 
                    currencycode_retailprice, buyLink, year, publisher
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                # Print the query and data tuple to check if they match
                print("SQL Query:", insert_query)
                print("Data Tuple:", data_tuple)

                cursor.execute(insert_query, data_tuple)
            except pymysql.MySQLError as e:
                # st.error(f"Error inserting record into MySQL: {e}")
                pass
        connection.commit()
        cursor.close()
        connection.close()

def main():
    # Streamlit UI
        st.title(":red[Data Harvesting and WareHousing] :book:")
        # Query input from user
        query = st.text_input("Enter a search query:")
    
        # Number of results to fetch
        max_results = st.slider("Number of results to fetch", 10, 1000, 100)
        books = fetch_books_paginated(query, max_results_per_page=40, total_results=max_results)
    
        # Button to trigger book fetching
        if st.button("Fetch Books"):
            with st.spinner("Fetching books..."):
                if books:
                    display_books(books)
                else:
                    st.error("Please provide the book catorgies in Search key")

        if st.button("load to MYSQL"):
            with st.spinner("Inserting book into MYSQL Workbench....."):
                books1 = fetch_books_paginated(query, max_results_per_page=40, total_results=max_results)
                if books:
                    insert_books_into_mysql(books)
                    st.success("Data inserted into MySQL database successfully!")
                else:
                    st.error("data miss match or data already been inserted.")

if __name__ == "__main__":
    main()

import pymysql
import pandas as pd
import streamlit as st

# MySQL connection setup with PyMySQL
def connect_to_mysql():
    connection = pymysql.connect(
        host="localhost",        # Your MySQL host
        user="root",             # Your MySQL username
        password="mysql",       # Your MySQL password
        database="book_details", # Your MySQL database name
        cursorclass=pymysql.cursors.DictCursor  # This ensures the result is returned as a dictionary
    )
    return connection

# Function to fetch data from a query
def fetch_data_from_query(query):
    connection = connect_to_mysql()
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
    connection.close()
    return df

# List of queries and their associated questions
queries = [
    """SELECT CASE WHEN isEbook = True THEN 'eBook' ELSE 'Physical Book' END AS book_format, saleability,  COUNT(*) AS available_count FROM books_details GROUP BY book_format, saleability ORDER BY book_format;""",
    """SELECT publisher, COUNT(*) AS book_count FROM books_details WHERE publisher NOT IN ('N/A') GROUP BY publisher ORDER BY book_count DESC LIMIT 5;""",
    """SELECT publisher, AVG(averageRating) AS avg_rating FROM books_details WHERE publisher NOT IN ('N/A') AND averageRating NOT IN ('N/A') GROUP BY publisher ORDER BY avg_rating DESC LIMIT 5;""",
    """SELECT book_title, amount_retailPrice, currencycode_retailprice FROM books_details WHERE amount_retailPrice IS NOT NULL ORDER BY amount_retailPrice DESC LIMIT 5;""",
    """SELECT book_title, year, pageCount FROM books_details WHERE year > 2010 AND pageCount >= 500 AND year NOT IN ('N/A') AND pageCount IS NOT NULL ORDER BY 2, 3 desc;""",
    """SELECT book_title, amount_listPrice, amount_retailPrice, ( (amount_listPrice - amount_retailPrice) / amount_listPrice ) * 100 AS discount_percentage FROM books_details WHERE amount_listPrice IS NOT NULL AND amount_retailPrice IS NOT NULL AND ((amount_listPrice - amount_retailPrice) / amount_listPrice) * 100 > 20 ORDER BY discount_percentage DESC;""",
    """SELECT CASE WHEN isEbook = True THEN 'eBook' ELSE 'Physical Book' END AS book_format, AVG(pageCount) AS avg_page_count FROM books_details WHERE pageCount IS NOT NULL AND pageCount > 0 GROUP BY book_format;""",
    """SELECT book_authors, COUNT(book_id) AS number_of_books FROM books_details where book_authors not in ('N/A') GROUP BY book_authors ORDER BY number_of_books DESC LIMIT 3;""",
    """SELECT publisher, COUNT(book_id) AS number_of_books FROM books_details WHERE publisher not in ('Not available') GROUP BY publisher HAVING COUNT(book_id) > 10;""",
    """SELECT categories, AVG(pageCount) AS average_page_count FROM books_details where categories not in ('N/A') GROUP BY categories;""",
    """SELECT book_id, book_title, book_authors, pageCount, categories, language, ratingsCount, averageRating, publisher FROM books_details WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;""",
    """SELECT book_id, book_title, book_authors, ratingsCount, averageRating, publisher FROM books_details WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM books_details);""",
    """SELECT b1.book_id, b1.book_title, b1.book_authors, b1.year, b1.publisher FROM books_details b1 JOIN books_details b2 ON b1.book_authors = b2.book_authors AND b1.year = b2.year AND b1.book_id != b2.book_id WHERE b1.book_authors NOT IN ('N/A') ORDER BY b1.book_authors, b1.year, b1.book_title;""",
    """SELECT book_id, book_title, book_subtitle, book_authors, year, publisher FROM books_details WHERE book_title LIKE '%Python%' ORDER BY book_title;""",
    """SELECT year, AVG(amount_listPrice) AS average_price FROM books_details GROUP BY year ORDER BY average_price DESC LIMIT 5;""",
    """SELECT COUNT(DISTINCT book_authors) AS authors_with_consecutive_years FROM (SELECT book_authors, year FROM books_details GROUP BY book_authors, year HAVING MAX(year) - MIN(year) = 2 AND COUNT(DISTINCT year) = 3) AS consecutive_authors;""",
    """SELECT book_authors, year, COUNT(DISTINCT book_id) AS book_count FROM books_details where book_authors not in ('N/A') GROUP BY book_authors, year HAVING COUNT(DISTINCT publisher) > 1;""",
    """SELECT AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice END) AS avg_ebook_price, AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice END) AS avg_physical_price FROM books_details;""",
    """WITH rating_stats AS (SELECT AVG(averageRating) AS avg_rating, STDDEV(averageRating) AS stddev_rating FROM books_details) SELECT book_title, averageRating, ratingsCount FROM books_details JOIN rating_stats WHERE averageRating > (avg_rating + 2 * stddev_rating) OR averageRating < (avg_rating - 2 * stddev_rating);""",
    """WITH publisher_avg_ratings AS (SELECT publisher, AVG(averageRating) AS avg_rating, COUNT(book_id) AS book_count FROM books_details GROUP BY publisher HAVING COUNT(book_id) > 10) SELECT publisher, ROUND(avg_rating, 2) AS avg_rating, book_count FROM publisher_avg_ratings ORDER BY avg_rating DESC LIMIT 5;"""
    # Add more queries (total 20 queries)
]

questions = {
    queries[0]: "1.Check Availability of eBooks vs Physical Books",
    queries[1]: "2.Find the Publisher with the Most Books Published",
    queries[2]: "3.Identify the Publisher with the Highest Average Rating",
    queries[3]: "4.Get the Top 5 Most Expensive Books by Retail Price",
    queries[4]: "5.Find Books Published After 2010 with at Least 500 Pages",
    queries[5]: "6.List Books with Discounts Greater than 20%",
    queries[6]: "7.Find the Average Page Count for eBooks vs Physical Books",
    queries[7]: "8.Find the Top 3 Authors with the Most Books",
    queries[8]: "9.List Publishers with More than 10 Books",
    queries[9]: "10.Find the Average Page Count for Each Category",
    queries[10]: "11.Retrieve Books with More than 3 Authors",
    queries[11]: "12.Books with Ratings Count Greater Than the Average",
    queries[12]: "13.Books with the Same Author Published in the Same Year",
    queries[13]: "14.Books with a Specific Keyword in the Title",
    queries[14]: "15.Year with the Highest Average Book Price",
    queries[15]: "16.Count Authors Who Published 3 Consecutive Years",
    queries[16]: "17.Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year.",
    queries[17]: "18.Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries.",
    queries[18]: "19.Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.",
    queries[19]: "20.Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published."
    # Add corresponding questions for other queries here
}

# Streamlit UI
def main():
    st.title(":red[Data Visualization] :bar_chart:")
    
    # Dropdown to select question (query)
    selected_question = st.selectbox("Select a question to fetch data", list(questions.values()))
    
    # Get the corresponding query for the selected question
    selected_query = [query for query, question in questions.items() if question == selected_question][0]
    
    # Display the associated query
    st.write("**SQL Query:**", selected_query)
    
    # Fetch data from the selected query
    if selected_query:
        data = fetch_data_from_query(selected_query)
        
        # Display the results as a table
        if not data.empty:
            st.write("Query Results:")
            st.dataframe(data)
        else:
            st.write("No data returned for this query.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
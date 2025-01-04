create database Book_details;
use Book_details;

SELECT * FROM book_details.books_details;

SELECT count(*) FROM book_details.books_details;

CREATE TABLE IF NOT EXISTS books_details (
book_id VARCHAR(255) PRIMARY KEY,
search_key VARCHAR(255),
book_title VARCHAR(255), 
book_subtitle TEXT,
book_authors TEXT,
book_description TEXT,
industryIdentifiers TEXT,
text_readingModes BOOLEAN,
image_readingModes BOOLEAN, 
pageCount INT,
categories TEXT, 
language VARCHAR(50), 
imageLinks TEXT,
ratingsCount INT,
averageRating dec(3,2),
country VARCHAR(50),
saleability VARCHAR(50),
isEbook BOOLEAN, 
amount_listPrice dec(10,2),
currencyCode_listPrice VARCHAR(50),
amount_retailPrice dec(10,2),
currencycode_retailprice VARCHAR(50),
buyLink TEXT,
year TEXT,
publisher TEXT
);


Select * from books_details;

#1st query
SELECT 
    CASE 
        WHEN isEbook = True THEN 'eBook'
        ELSE 'Physical Book'
    END AS book_format,
    saleability,  COUNT(*) AS available_count
FROM books_details
GROUP BY book_format, saleability
ORDER BY book_format;

#2nd query
SELECT publisher, COUNT(*) AS book_count
FROM books_details
WHERE publisher NOT IN ('N/A')
GROUP BY publisher
ORDER BY book_count DESC
LIMIT 5;

#3rd query
SELECT publisher, AVG(averageRating) AS avg_rating
FROM books_details
WHERE publisher NOT IN ('N/A') AND averageRating NOT IN ('N/A')
GROUP BY publisher
ORDER BY avg_rating DESC
LIMIT 5;

#4th query
SELECT book_title, amount_retailPrice, currencycode_retailprice
FROM books_details
WHERE amount_retailPrice IS NOT NULL  -- Ensure we're only considering books with a retail price
ORDER BY amount_retailPrice DESC  -- Sort by retail price in descending order
LIMIT 5; 

#5th Query
SELECT book_title, year, pageCount
FROM books_details
WHERE year > 2010
  AND pageCount >= 500
  AND year NOT IN ('N/A')
  AND pageCount IS NOT NULL
ORDER BY 2, 3 desc;

#6th Query
SELECT book_title, amount_listPrice, amount_retailPrice, 
       ( (amount_listPrice - amount_retailPrice) / amount_listPrice ) * 100 AS discount_percentage
FROM books_details
WHERE amount_listPrice IS NOT NULL 
  AND amount_retailPrice IS NOT NULL
  AND ((amount_listPrice - amount_retailPrice) / amount_listPrice) * 100 > 20
ORDER BY discount_percentage DESC;

#7th query
SELECT 
    CASE 
        WHEN isEbook = True THEN 'eBook'
        ELSE 'Physical Book'
    END AS book_format,
    AVG(pageCount) AS avg_page_count
FROM 
    books_details
WHERE 
    pageCount IS NOT NULL AND pageCount > 0
GROUP BY 
    book_format;
    
# 8th query
SELECT 
    book_authors,
    COUNT(book_id) AS number_of_books
FROM 
    books_details
    where book_authors not in ('N/A')
GROUP BY 
    book_authors
ORDER BY 
    number_of_books DESC
LIMIT 3;

#9th query
SELECT 
    publisher,
    COUNT(book_id) AS number_of_books
FROM 
    books_details
    WHERE publisher not in ('Not available')
GROUP BY 
    publisher
HAVING 
    COUNT(book_id) > 10;

#10th query
SELECT 
    categories,
    AVG(pageCount) AS average_page_count
FROM 
    books_details
    where categories not in ('N/A')
GROUP BY 
    categories;
    
#11TH QUERY
SELECT 
    book_id, 
    book_title, 
    book_authors, 
    pageCount, 
    categories, 
    language, 
    ratingsCount, 
    averageRating, 
    publisher
FROM 
    books_details
WHERE 
    LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;

#12TH QUERY
SELECT 
    book_id, 
    book_title, 
    book_authors, 
    ratingsCount, 
    averageRating, 
    publisher
FROM 
    books_details
WHERE 
    ratingsCount > (SELECT AVG(ratingsCount) FROM books_details);

#13TH QUERY
SELECT 
    b1.book_id,
    b1.book_title,
    b1.book_authors,
    b1.year,
    b1.publisher
FROM 
    books_details b1
JOIN 
    books_details b2
    ON b1.book_authors = b2.book_authors
    AND b1.year = b2.year
    AND b1.book_id != b2.book_id
    WHERE b1.book_authors NOT IN ('N/A')
ORDER BY 
    b1.book_authors, b1.year, b1.book_title;

#14TH QUERY
SELECT 
    book_id,
    book_title,
    book_subtitle,
    book_authors,
    year,
    publisher
FROM 
    books_details
WHERE 
    book_title LIKE '%Python%'
ORDER BY 
    book_title;

#15TH QUERY
SELECT 
    year, 
    AVG(amount_listPrice) AS average_price
FROM 
    books_details
GROUP BY 
    year
ORDER BY 
    average_price DESC
LIMIT 5;

#16TH QUERY
SELECT 
    COUNT(DISTINCT book_authors) AS authors_with_consecutive_years
FROM (
    SELECT 
        book_authors,
        year
    FROM 
        books_details
    GROUP BY 
        book_authors, year
    HAVING
        MAX(year) - MIN(year) = 2
        AND COUNT(DISTINCT year) = 3
) AS consecutive_authors;

#17TH QUERY
SELECT 
    book_authors, 
    year, 
    COUNT(DISTINCT book_id) AS book_count
FROM 
    books_details
    WHERE book_authors not in ('N/A')
GROUP BY 
    book_authors, year
HAVING 
    COUNT(DISTINCT publisher) > 1;

#18TH QUERY
SELECT
    AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice END) AS avg_ebook_price,
    AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice END) AS avg_physical_price
FROM 
    books_details;

#19TH QUERY
WITH rating_stats AS (
    SELECT 
        AVG(averageRating) AS avg_rating,
        STDDEV(averageRating) AS stddev_rating
    FROM books_details
)
SELECT 
    book_title, 
    averageRating, 
    ratingsCount
FROM 
    books_details
JOIN 
    rating_stats
WHERE 
    averageRating > (avg_rating + 2 * stddev_rating)
    OR averageRating < (avg_rating - 2 * stddev_rating);
    
#20TH QUERY
WITH publisher_avg_ratings AS (
    SELECT 
        publisher,
        AVG(averageRating) AS avg_rating,
        COUNT(book_id) AS book_count
    FROM 
        books_details
    GROUP BY 
        publisher
    HAVING 
        COUNT(book_id) > 10
)
SELECT 
    publisher,
    ROUND(avg_rating, 2) AS avg_rating,
    book_count
FROM 
    publisher_avg_ratings
ORDER BY 
    avg_rating DESC
LIMIT 5;


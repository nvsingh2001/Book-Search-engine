# Book-Search-engine

The Book Search Web App is a simple Flask application designed to help users search through a collection of books using an inverted index and a basic search engine. The application allows users to enter search queries and retrieves relevant book results based on the provided query.

## Key Features:

- **Search Interface:** Users can input search queries through a user-friendly web interface.
- **Search Results:** Relevant book results are displayed in a paginated format, providing users with information about the title, author, and relevance score.
- **Preprocessing:** The application preprocesses book data, including titles, authors, and descriptions, by removing punctuation, converting to lowercase, removing stop words, and stemming words to improve search accuracy.
- **Inverted Index:** The application uses an inverted index data structure to efficiently index book data, allowing for fast retrieval of relevant results.
- **Scalability:** The application is designed to handle a large volume of book data and can scale to accommodate additional features and functionalities in the future.

## Technologies Used:

- **Python:** The backend logic of the application is implemented in Python using the Flask framework.
- **HTML:** The frontend user interface is built using HTML for structure and CSS for styling.

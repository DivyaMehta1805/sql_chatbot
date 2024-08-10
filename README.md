# SQL_CHATBOT
A database chatbot, utilizing:
   - **LLM** (`Llama-3.1-70b`) for converting Natural Language to SQL & SQL result to NL 
   - **SQLite3 db** for storage & querying
   - **Vector Embeddings** for tag generation based on similarity, via `Sentence Transformers`
   - **SpaCy** for query preprocessing & parsing semantic structure 

![image](https://github.com/user-attachments/assets/fed9d280-b2a1-4dc5-b933-a9163448fc17)

# Instructions to Run
1. Python API (tested with Python3.11)
    - (Optional) Create a virtual environment
    - Install requirements by `pip install -r requirements.txt`
    - Start the server by running `python python_apisetup.py`
    - Please make sure that `GROQ_API_KEY` environment variable is set. If not, please obtain a free API key from Groq.

2. Frontend:
    - Go to frontend `cd frontend` 
    - Install node modules `npm i`
    - Start the frontend: `npm start`

You should be able to run it as below:

# Video Demo
![Video Demonstration] (https://github.com/DivyaMehta1805/sql_chatbot/raw/main/sql_rag-main/nl2sql.mp4)

# API & Preprocessing Rationale
## Preprocessing: Challenges & Solutions
1. **Introduced a similar terms column in events and Companies schema**
   - **Challenge**: Company industry (and similarly relevant industries for an event) are bad candidates for exact matching. e.g. `oil & gas` industry and `petroleum` industry are related 
   - **Solution**: Created Exhaustive *Vector Embeddings* for each unique company industry derived from the `company_industries` column. For each event/company description, ran a *similarity search* using an embedding model `all-MiniLM-L6-v2`, and created tags for each event/each company. 

2. **Handling Employee Ranges**:
   - **Challenge**: Irregular Formatting for Employees column (e.g. `50-200`)
   - **Solution**: Store upper & lower limits of employee count instead and deleted the previous column.

3. **Email Address Generation**:
   - **Challenge**: Irregular email formatting, e.g. `[first][last]` and `[firstinitial][last]`, etc.
   - **Solution**: Compute the email ID's precisely by writing & running a simple Python script
     
4. **Standardized revenue to filter out irrelevant comparisons**: 
   - **Challenge**: Revenue description in different denomenations (e.g. `billions` vs `millions`)
   - **Solution**: Converted all revenue to `millions`

## Main Functionalities of the API
1. **Natural Language Processing of query Using SpaCy**:
   - **Contextual Query Analysis**: Uses *`SpaCy`* to analyze and determine whether context is for companies or events. 
   
   - Helps in queries like `The list of sales events being attended by finance companies` 
   - LLM has confusion dealing with such cases. SpaCy helps provide the relevant context:
      - Is a particular adjective for Events or for Companies?, e.g. `Sales Events` and `Finance Companies`
      - When both events and companies are involved, whether to take a union or an intersection?
      - This context is then used by the llm to make the right decision.

2. **Search Similar Chunks**: Uses tags column in databases to search for similar terms as well when the search involves a particular industry. 
     
3. **SQL Query Generation**: Uses an LLM (`Llama-3.1-70b` via Groq; but plug'n'play with any OpenAI compatible API) to generate `NL-2-SQL` and then from SQL Result to Natural Language.

4. **Flask API Deployment**:
   - Includes endpoints for processing natural language queries (`/api/query`) and retrieving results (`/api/result`), supporting JSON input and output.

## API: Key Challenges and Solutions

1. **Irrelevant Results Without Vector Embeddings**:
   - **Challenge**: When searching for a particular industry, the LLM generated queries for precise matching, leaving out industries with similar names.
   - **Solution**: Implemented vector embeddings for relevant data and applied threshold-based filtering to capture nuanced relationships.

2. **Enhancing Contextual Understanding Using SpaCy**:
   - **Challenge**: LLM had problems understanding the relationship between Adjectives (e.g. `finance related`) and Nouns (`events` vs `companies`)
   - **Solution**: Used SpaCy to analyze adjectives and nouns in queries, directing searches to the correct category and improving result relevance.

## Back-End Improvement Plan

1. **Enhancing Synonym Handling with WordNet**:
   - **Plan**: Integrate `WordNet` to identify synonyms for terms in the "Similar Terms" column, creating a comprehensive list of related terms for more accurate search results.

2. **Query Matching (RAG) with Pre-Generated SQL Queries**:
   - Maintain a list of pre-generated SQL queries to refine query processing and improve result accuracy.
   - **What**: Apply RAG for more accurate Query Context
   - **How**: Queries will be matched against a pre-generated list of `Natural Language Query - SQL query` tuples to find a close match. Providing further context (`n-shot`) [can help with better generation](https://arxiv.org/abs/2005.14165)


# UI

## Key Functionalities

1. **Query Submission**: User enters query which are then taken to the backend by the POST operation.
   
3. **Data Retrieval and Display**:
   - **Fetching Results**: Makes a POST request to `/api/query` and fetches results from `/api/result`.
   - **Displaying Results**: Shows user queries and backend responses in a chat-like interface.

4. **Loading Indicators**:
   - Shows loading state unless the answer is updated. For this I have a `useState` which stores the most recent answer. The functionality rechecks 5 times at constant intervals and gives the answer only once it is updated from the backend.

5. **UI Styling**:
   - **Theming**: Applies a consistent theme with Material-UI’s ThemeProvider.

## API Endpoints Used

1. **POST Request to Submit Query**:
   - **Endpoint**: `http://127.0.0.1:5000/api/query`
   - **Method**: POST
   - **Body**: JSON object with user query.

2. **GET Request to Fetch Result**:
   - **Endpoint**: `http://127.0.0.1:5000/api/result`
   - **Method**: GET

## Key Challenges

1. **Data Retrieval Challenges**:
   - **Outdated Data Issue**: Implemented mechanisms to handle outdated data and show loading states. In the beginning since backend took time to refresh the data for the previous query was retrieved and displayed. Used useState for currentAns and multiple retries to avoid this and load the new Query Data only.

2. **Design Challenges**:
   - **User Experience**: Making the ui user friendly posed some challenges.

## Further Improvements

1. **Enhanced Data Retrieval**:
   - **Timestamp-Based Polling**: Use exponential polling with timestamps to ensure accurate data retrieval. This will not update until the backend refreshes and will also take care of an error response being shown to the user in case it never updates because it not only takes into consideration the current state of the answer but also the time stamp.


# Database

## Schema

1. **Events Table**
   - Contains all columns from `event_info.csv`
   - `event_start_date` (DATE): The start date of the event, stored in 'YYYY-MM-DD' format
   - `event_end_date` (DATE): The end date of the event, stored in 'YYYY-MM-DD' format
   - `similar_terms` containing all industry types pertaining to the event description
2. **Companies Table**:
   - Columns from `company_info.csv`
   - `similar_terms`: containing all industry types pertaining to the company description
   - `employee_range_lower`: lower limit of the Employee count range
   - `employee_range_upper`: upper limit of the employee count range
   - `revenue_millions`: Revenue of the company in millions
3. **People Table**:
   - Columns from `people_info.csv`



## Challenges

1. **Handling Diverse Data Formats**:
   - **Inconsistent Revenue Figures**: Standardized revenue data (in millions) to avoid confusion.
   - **Employee Range Confusion**: Split ranges into lower and upper bounds so as to avoid irrelevant results.

2. **Generating and Managing Email Addresses**:
   - Programmatically created email addresses ensuring proper formatting.

3. **Irrelevant Industry Comparisons**:
   - Removed the company_industry column to prevent misleading comparisons.

## Improvements

1. **Identifying Key Query Components and Indexing**:
   - Optimize join operations and reduce query complexity by indexing relevant columns. For ex: company event_url column and event_url column in events are joined almost in every other query. Indexing them in the future would greatly enhance performance I believe.

2. **Advanced Similarity Matching System**:
   - Implement a dynamic similarity matching algorithm to improve accuracy.

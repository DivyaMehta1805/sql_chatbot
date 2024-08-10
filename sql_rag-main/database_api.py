import sqlite3
import pandas as pd
import groq
import os
import spacy
# If it doesn't work please run: {python -m spacy download en_core_web_sm}
nlp = spacy.load('en_core_web_sm')
combined_response=""
# Assuming you've set your Groq API key as an environment variable
groq_api_key = os.environ.get("GROQ_API_KEY")
client = groq.Groq(api_key=groq_api_key)

def connect_to_db():
    return sqlite3.connect('events_database.db')

def query_db(query, params=None):
    conn = connect_to_db()
    try:
        if params:
            result = pd.read_sql_query(query, conn, params=params)
        else:
            result = pd.read_sql_query(query, conn)
        return result
    finally:
        conn.close()

def analyze_query(query):
    doc = nlp(query)
    event_indicators = ['event', 'conference', 'seminar', 'workshop', 'meetup', 'exhibition', 'trade show', 'symposium']
    company_indicators = ['company', 'business', 'corporation', 'firm', 'enterprise', 'organization', 'industry']
    
    event_context = False
    company_context = False
   
    # print(f"\nAnalyzing query: {query}")
    for token in doc:
        # print(f"Token: {token.text}, Lemma: {token.lemma_}, POS: {token.pos_}, Dep: {token.dep_}")
        # print(f"Children: {[f'{child.text} ({child.pos_})' for child in token.children]}")
        
        if token.lemma_.lower() in event_indicators:
            modifiers = [child for child in token.children if child.pos_ in ['ADJ'] or child.dep_ in ['compound', 'amod']]
            if modifiers:
                event_context = True
                print(f"Event context set to True. '{token.text}' modified by: {[m.text for m in modifiers]}")
        
        if token.lemma_.lower() in company_indicators:
            modifiers = [child for child in token.children if child.pos_ in ['ADJ'] or child.dep_ in ['compound', 'amod']]
            if modifiers:
                company_context = True
                print(f"Company context set to True. '{token.text}' modified by: {[m.text for m in modifiers]}")

    print(f"Final Event context: {event_context}")
    print(f"Final Company context: {company_context}")
    
    if event_context and company_context:
        return 'both'
    elif event_context:
        return 'event'
    elif company_context:
        return 'company'
    else:
        return 'unknown'

# Test cases
test_queries = [
    "find all finance events",
    "oil companies",
    "oil companies and cybersec events",
    "companies with more than 1000 employees",
    "events in New York",
    "tech startups",
    "companies greater than 1000",
]

for query in test_queries:
    result = analyze_query(query)
    print(f"\nQuery: {query}")
    print(f"Final result: {result}\n")
    
    

def generate_sql_query(natural_language_query):
    context = analyze_query(natural_language_query)
    
    prompt = f"""
You are given an SQL database with the following schema:
event_info contains following columns: event_logo_url,event_name,event_start_date,event_end_date,event_venue,event_country,event_description,event_url,similar_terms

companies contains following columns: company_logo_url,company_logo_text,company_name,relation_to_event,event_url,company_revenue,employee_range_lower,employee_range_upper,company_phone,company_founding_year,company_address,company_overview,homepage_url,linkedin_company_url,homepage_base_url,company_logo_url_on_event_page,company_logo_match_flag,similar_terms,revenue_millions

people contains following columns: first_name,middle_name,last_name,job_title,person_city,person_state,person_country,email,homepage_base_url,duration_in_current_job,duration_in_current_company

Given the following natural language query, generate ONLY an appropriate SQLite-compatible SQL query without any additional explanation. Do not print anything other than the query itself.

Events and company data can be merged using 'event_url' column.
Company and people data can be merged using 'homepage_base_url' column.
Each event_url corresponds to a unique event, and each homepage_base_url can be interpreted as a unique company.
Event Details:
1.event_name: Official name of the event
2.event_start_date: Date when the event begins
3.event_end_date: Date when the event concludes
4.event_venue:Specific location where the event is held
5.event_country: Country where the event takes place
6.event_description: A detailed summary of the event's purpose and content
7.event_url: The official website link for the event
8.event_logo_url: A URL to the event's logo image
9.similar_terms: Keywords or phrases related to event for search purposes
People Details:
1.first_name: The person's given name
2.middle_name: The person's middle name (if applicable)
3.last_name: The person's family name or surname
4.duration_in_current_job: How long they've been in their current role
5.duration_in_current_company: How long they've been with their current employer
6.person_city: The city where the person is located
7.person_state: The state or region where the person resides
8.person_country: The country where the person is based
9.email: The person's email address
Online Presence:
homepage_base_url: The root domain of the person's personal or professional website
IMPORTANT CHANGES:
1. When searching for companies based on employee count, use these new columns. For example:
   - To find companies with more than 1000 employees, use: WHERE employee_range_upper > 1000
   - To find companies with 50-200 employees, use: WHERE employee_range_lower >= 50 AND employee_range_upper <= 200
2. The 'company_revenue' column is now standardized in millions and stored in the 'revenue_millions' column.
3. When searching for companies based on revenue, use the 'revenue_millions' column.

IMPORTANT: When searching for relevant information, prioritize using the 'similar_terms' column in the event_info and companies tables. Use the following guidelines:
1. Ignore any delimiters in the 'similar_terms' column. Treat the entire column as a single text field.
2. Use case-insensitive partial matching for each relevant keyword from the query.
3. Search for keywords anywhere within the 'similar_terms' column, not just at the beginning or end of terms.
4. Include variations and related terms of the keywords in your search.
5. Use the LIKE operator with wildcards for flexible matching. For example:
   WHERE LOWER(companies.similar_terms) LIKE '%keyword1%'
     OR LOWER(companies.similar_terms) LIKE '%keyword2%'
     OR LOWER(companies.similar_terms) LIKE '%related_term%'
6. Only use direct column comparisons if there's no relevant match in the 'similar_terms' column.
CONTEXT INSTRUCTIONS:
The context of the query has been analyzed and determined to be: {context}
- If the context is 'company', search only in the similar_terms column of the companies table.
- If the context is 'event', search only in the similar_terms column of the event_info table.
- If the context is 'both', search in both tables and use INTERSECT to find common results in the similar_terms columns.
- If the context is 'unknown', search in both tables and use UNION to combine results from the similar_terms columns.
- If any context (event or company) is false, DO NOT SEARCH its corresponding similar_terms column.

Natural language query: {natural_language_query}

    SQL query:
    """  
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that generates SQL queries based on natural language inputs. Strictly follow the context instructions to determine which tables and columns to search."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-70b-versatile",
        temperature=0.1,
        max_tokens=300,
    )
    # print(f"Full prompt:\n{prompt}")
    # print(f"Raw API response:\n{response}")
    return response.choices[0].message.content.strip()
def summarize_query_result(sql_query, query_result):
    prompt = f"""
    Summarize the following SQL query result for an end user. Provide a clear, concise explanation of the data without technical jargon. Focus on the key insights and important information revealed by the query.

    SQL Query: {sql_query}

    Query Result:
    {query_result.to_string()}

    Your summary should:
    1. Highlight the main findings or insights from the data
    2. Be easy for a non-technical user to understand
    3. Be concise but include all relevant information

    Summary:
    """
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that summarizes SQL query results in a clear, non-technical manner for end users."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-70b-versatile",
        temperature=0.3,
        max_tokens=300,
    )
    
    return response.choices[0].message.content.strip()


def process(user_query):
    user_input = user_query
        
    if user_input.lower() == 'quit':
        return ""
        
    try:
        sql_query = generate_sql_query(user_input)
        print(f"Generated SQL query: {sql_query}")
            
        result = query_db(sql_query)
        print("\nQuery result:")
        print(result)
        summarize=summarize_query_result(user_input,result)
        print({summarize});
        
        return summarize
    except Exception as e:
            print(f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     main()

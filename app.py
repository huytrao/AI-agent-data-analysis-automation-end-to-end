import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Streamlit app title
st.title("AI Agent Data Analysis")

# File uploader with the default size limit
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"], accept_multiple_files=False)

if uploaded_file is not None:
    # Determine file type and read data
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        data = pd.read_excel(uploaded_file)
    
    # Display the uploaded data
    st.write("Uploaded Data:")
    st.dataframe(data)

    # Get user input to describe the data
    data_context = st.text_input("Describe detail your context of data")
    if data_context:
        st.write("User's Data Description:")
        st.write(data_context)
    
    # Get user input to define their problem 
    problem = st.text_input("Describe your problem or question:")
    if problem:
        st.write("User's Problem/Question:")
        st.write(problem)

    # Database connection details
    db_host = "localhost"  # Replace with the actual IP address of the PostgreSQL container
    db_port = "5432"
    db_name = "n8n"  # Replace with your database name
    db_user = "n8n"  # Replace with your PostgreSQL username
    db_password = "n8n"  # Replace with your PostgreSQL password

    # Create a SQLAlchemy engine
    try:
        engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    except Exception as e:
        st.error("Failed to connect to the database. Please check your connection settings.")
        st.write(f"Error details: {e}")
        engine = None  # Set engine to None to prevent further errors

    # Add this before the button
    table_name = "uploaded_data"

    # Save data and problem/description to PostgreSQL
    if st.button("Save to Database"):
        if engine is None:
            st.error("Database connection is not available. Cannot save data.")
        else:
            # Save uploaded data to the specified table
            if table_name:
                try:
                    with engine.connect() as conn:
                        # Delete existing data from the table
                        conn.execute(text(f"DELETE FROM {table_name};"))
                    
                    # Insert new data into the table
                    data.to_sql(table_name, engine, if_exists="append", index=False)
                    st.success(f"Data successfully deleted and inserted into table '{table_name}' in PostgreSQL!")
                except Exception as e:
                    st.error("Failed to delete and insert data in the database.")
                    st.write(f"Error details: {e}")
            else:
                st.error("Please enter a valid table name.")
            
            # Save problem description to a separate table
            if problem:
                try:
                    problem_table_name = "problem_table"
                    with engine.connect() as conn:
                        conn.execute(text(f"TRUNCATE TABLE {problem_table_name} RESTART IDENTITY;"))
                    problem_data = pd.DataFrame({"problem": [problem]})
                    problem_data.to_sql(problem_table_name, engine, if_exists="replace", index=False)
                    st.success(f"Problem successfully replaced in table '{problem_table_name}' in PostgreSQL!")
                except Exception as e:
                    st.error("Failed to replace problem in the database.")
                    st.write(f"Error details: {e}")
            
            # Save data description to a separate table
            if data_context:
                try:
                    context_table_name = "context_table"
                    with engine.connect() as conn:
                        conn.execute(text(f"TRUNCATE TABLE {context_table_name} RESTART IDENTITY;"))
                    context_data = pd.DataFrame({"context": [data_context]})
                    context_data.to_sql(context_table_name, engine, if_exists="replace", index=False)
                    st.success(f"Context successfully replaced in table '{context_table_name}' in PostgreSQL!")
                except Exception as e:
                    st.error("Failed to replace context in the database.")
                    st.write(f"Error details: {e}")
    
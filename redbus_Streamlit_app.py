import streamlit as st
import psycopg2
import pandas as pd

# Database connection
connection = psycopg2.connect(
    database="Redbus",
    user="postgres",
    password="12345678",
    host="localhost",
    port="5432"
)
cur = connection.cursor()

# Query to fetch available columns
available_col = """
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'bus_routes';
"""

cur.execute(available_col)
col = cur.fetchall()
col = [str(x[0]) for x in col]

st.logo("https://s3.rdbuz.com/Images/rdc/rdc-redbus-logo.webp")
st.sidebar.text("RedBus mini project")
# st.image("https://s3.rdbuz.com/images/webplatform/india/Homepage-header-800.webp")
st.image("https://s3.rdbuz.com/images/webplatform/india/Homepage-header-1600.webp")
st.title("Redbus Filter and Sorting System")

# Multiselect for required columns
selected_col = st.multiselect("Select Required Columns", col)

if selected_col:
    query_select_col = ", ".join(selected_col)
    st.write("Selected Columns:", query_select_col)
else:
    query_select_col = "*"

# Defining filtering conditions
conditions = [
    "greater than", "greater than or equal to", "less than",
    "lesser than or equal to", "equal to", "not equal to",
    "contains", "does not contain", "between",
    "on", "on or before", "on or after",
    "before", "after"
]

# Filter management
def manage_filters():
    if 'filters' not in st.session_state:
        st.session_state.filters = []
    if 'filter_count' not in st.session_state:
        st.session_state.filter_count = 1

    st.sidebar.title("Manage Filters")
    
    for i in range(len(st.session_state.filters)):
        with st.sidebar.container():
            st.markdown(f"**Filter {i + 1}**")
            
            # Column selection
            column_name = st.selectbox(
                f"Select Column {i + 1}",
                col,
                key=f"column_selectbox{i}",
                index=col.index(st.session_state.filters[i]['column'])
                if st.session_state.filters[i]['column'] in col else 0
            )
            st.session_state.filters[i]['column'] = column_name
            
            # Condition selection
            condition = st.selectbox(
                f"Select Condition {i + 1}",
                conditions,
                key=f"condition_selectbox{i}",
                index=conditions.index(st.session_state.filters[i]['condition'])
                if st.session_state.filters[i]['condition'] in conditions else 0
            )
            st.session_state.filters[i]['condition'] = condition
            
            # Value input
            value = st.text_input(
                f"Enter Value {i + 1}",
                key=f"value_input{i}",
                value=st.session_state.filters[i]['value']
            )
            st.session_state.filters[i]['value'] = value
            
            # Second value for "between" condition
            if condition == "between":
                value_2 = st.text_input(
                    f"Enter Second Value {i + 1}",
                    key=f"value_input_2{i}",
                    value=st.session_state.filters[i].get('value_2', "")
                )
                st.session_state.filters[i]['value_2'] = value_2
            
            # Remove filter button
            if st.button(f"Remove Filter {i + 1}", key=f"remove_filter{i}"):
                st.session_state.filters.pop(i)
                st.session_state.filter_count -= 1
                st.rerun()

    # Add new filter button
    if st.sidebar.button("Add New Filters"):
        st.session_state.filters.append({'column': col[0], 'condition': conditions[0], 'value': "", 'value_2': ""})
        st.session_state.filter_count += 1
        st.rerun()

    return st.session_state.filters

# Sorting options
st.sidebar.title("Sorting Options")
sort_column = st.sidebar.selectbox("Sort By", col)
sort_order = st.sidebar.radio("Order", ["Ascending", "Descending"])

# Get filters from the sidebar
filter_conditions = manage_filters()

# Initialize pagination in session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None

# Construct the query
Select_query = f"SELECT {query_select_col} FROM bus_routes"
if st.button("Run"):
    final_query = []
    for f in st.session_state.filters:
        if f['condition'] == "greater than":
            query = f"{f['column']} > {f['value']}"
        elif f['condition'] == "greater than or equal to":
            query = f"{f['column']} >= {f['value']}"
        elif f['condition'] == "less than":
            query = f"{f['column']} < {f['value']}"
        elif f['condition'] == "lesser than or equal to":
            query = f"{f['column']} <= {f['value']}"
        elif f['condition'] == "equal to":
            query = f"{f['column']} = '{f['value']}'"
        elif f['condition'] == "not equal to":
            query = f"{f['column']} != '{f['value']}'"
        elif f['condition'] == "contains":
            query = f"{f['column']} LIKE '%{f['value']}%'"
        elif f['condition'] == "does not contain":
            query = f"{f['column']} NOT LIKE '%{f['value']}%'"
        elif f['condition'] == "between":
            query = f"{f['column']} BETWEEN '{f['value']}' AND '{f['value_2']}'"
        elif f['condition'] == "on":
            query = f"{f['column']} = '{f['value']}'"
        elif f['condition'] == "on or before":
            query = f"{f['column']} <= '{f['value']}'"
        elif f['condition'] == "on or after":
            query = f"{f['column']} >= '{f['value']}'"
        elif f['condition'] == "before":
            query = f"{f['column']} < '{f['value']}'"
        elif f['condition'] == "after":
            query = f"{f['column']} > '{f['value']}'"
        final_query.append(query)

    if final_query:
        Select_query += " WHERE " + " AND ".join(final_query)
    
    sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
    Select_query += f" ORDER BY {sort_column} {sort_direction}"

    cur.execute(Select_query)
    filtered_data = cur.fetchall()

    # Save the filtered data into session state
    st.session_state.filtered_data = pd.DataFrame(filtered_data, columns=query_select_col.split(", "))
    st.session_state.current_page = 1  # Reset to the first page

# Check if filtered data is available
if st.session_state.filtered_data is not None:
    df_filtered_data = st.session_state.filtered_data

    # Paginate results
    # df_filtered_data = pd.DataFrame(filtered_data, columns=query_select_col.split(", "))
    # st.write("Filtered Data")
    rows_per_page = 10
    total_rows = len(df_filtered_data)
    total_pages = (total_rows - 1) // rows_per_page + 1

    # Display the current page's data
    start_idx = (st.session_state.current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    st.dataframe(df_filtered_data.iloc[start_idx:end_idx])

    # Pagination controls at the bottom
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("Previous"):
            if st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
    with col3:
        if st.button("Next"):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()
    with col2:
        st.write(f"Page {st.session_state.current_page} of {total_pages}")

    # Download button at the top-right
    # st.sidebar.download_button
    st.download_button(
        label="Download Filtered Data",
        data=df_filtered_data.to_csv(index=False),
        file_name="filtered_data.csv",
        mime="text/csv"
    )

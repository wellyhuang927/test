import streamlit as st
import pandas as pd
# from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px

# Set page configuration to wide mode
st.set_page_config(
    layout="wide"  # Set the layout to wide mode
)

# Streamlit app
st.title('TEST')

# Add custom CSS for font sizes and input box styling
st.markdown("""
    <style>
        .big-font {
            font-size: 24px !important;
            color: #333;
        }
        .medium-font {
            font-size: 18px !important;
            color: #666;
        }
        .text-input-label {
            font-size: 24px !important;
            color: #333;
        }
        .dataframe {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: #f9f9f9;
        }
        .text-input {
            font-size: 18px !important;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #007bff;
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# File uploader widget with larger font
st.markdown('<p class="big-font">Upload the JIRA file</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("")

if uploaded_file is not None:
    
    data = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")

    # Performance Metric Calculation
    relevant_columns = ['Summary', 'Issue key', 'Issue Type', 'Status', 'Priority', 'Project key', 'Project name', 'Project type', 'Project lead', 'Created', 'Resolved', 'Comment']
    performance_data = data[relevant_columns]
    performance_data['Comment'] = performance_data['Comment'].fillna('')
    performance_data['Employee ID'] = performance_data['Comment'].apply(lambda x: x.split(';')[1] if ';' in x else None)
    performance_data = performance_data[performance_data['Employee ID'].notnull()]
    performance_data['Created'] = pd.to_datetime(performance_data['Created'])
    performance_data['Resolved'] = pd.to_datetime(performance_data['Resolved'])
    performance_data['Completion Time'] = (performance_data['Resolved'] - performance_data['Created']).dt.total_seconds() / 3600  # Convert to hours

    performance_data['Priority'] = performance_data['Priority'].fillna('Low')  # Assuming 'Low' priority for missing values
    performance_data['Is Priority'] = performance_data['Priority'].isin(['High', 'Highest'])
    performance_data['Is Completed'] = performance_data['Status'] == 'Done'
    performance_data['Is Blocked'] = performance_data['Status'] == 'Blocked'
    employee_performance = performance_data.groupby('Employee ID').agg({
        'Issue key': 'count',
        'Is Completed': 'sum',
        'Is Blocked': 'sum',
        'Completion Time': 'mean',
        'Issue Type': 'nunique',
        'Priority': lambda x: x.value_counts().to_dict(),
        'Comment': 'count'
    }).rename(columns={
        'Issue key': 'Tasks Total',
        'Is Completed': 'Tasks Completed',
        'Is Blocked': 'Tasks Blocked',
        'Completion Time': 'Average Completion Time',
        'Issue Type': 'Story Types Handled',
        'Priority': 'Priority Types Handled',
        'Comment': 'Comments Received'
    })
    employee_performance.reset_index(inplace=True)
    employee_performance['Average Completion Time'] = employee_performance['Average Completion Time'].round().astype(int)

    # Display part

    # Dropdown for selecting employee
    selected_employee = st.selectbox(
        'Select an employee',
        options=employee_performance['Employee ID'].unique(),
        index=0  # Select first employee by default
    )

    # If an employee is selected, display the relevant information
    if selected_employee:
        filtered_data = employee_performance[employee_performance['Employee ID'] == selected_employee]
        tasks_total = filtered_data['Tasks Total'].values[0]
        tasks_completed = filtered_data['Tasks Completed'].values[0]
        tasks_blocked = filtered_data['Tasks Blocked'].values[0]
        avg_completion_time = filtered_data['Average Completion Time'].values[0]
        priority_types_handled = filtered_data['Priority Types Handled'].values[0]
        comments_received = filtered_data['Comments Received'].values[0]

        # Displaying the leaderboard information
        st.markdown(f"### Employee Performance for {selected_employee}")
        leaderboard = pd.DataFrame({
            'Employee ID': [selected_employee],
            'Tasks Completed': [tasks_completed],
            'Tasks Blocked': [tasks_blocked],
            'Tasks Total': [tasks_total],
            'Average Completion Time (hours)': [avg_completion_time]
        })
        st.table(leaderboard)

        # Displaying the priority pie chart
        priority_labels = list(priority_types_handled.keys())
        priority_values = list(priority_types_handled.values())
        priority_fig = px.pie(values=priority_values, names=priority_labels, title="Types of Priorities Handled")
        st.plotly_chart(priority_fig)

        # Displaying the comments information
        st.markdown(f"### Comments for {selected_employee}")
        st.markdown(f"Number of Comments: {comments_received}")

else:
    st.info("Please upload a valid JIRA file to proceed.")

















# # Visualize (test)
# if not employee_performance.empty:
#     fig = px.bar(employee_performance, x='Employee ID', y='Tasks Completed', title='Tasks Completed per Employee', labels={'Tasks Completed': 'Number of Tasks'})
#     st.plotly_chart(fig)

# priority_filter = st.multiselect('Select Priority', options=performance_data['Priority'].unique(), default=performance_data['Priority'].unique())
# filtered_data = performance_data[performance_data['Priority'].isin(priority_filter)]

# st.markdown("### Employee Performance Summary")
# st.dataframe(employee_performance)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

def change_state():
    st.session_state.plot = None
    st.session_state.stats = None
    st.session_state.warning = None
    
st.set_page_config(page_title="EZ Plots", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)    
st.title("EZ Plots")
st.sidebar.title("Toolbar")
# uploaded_files = st.file_uploader("Drag and drop your CSV file here", accept_multiple_files=True, type=["csv"], key="file_uploader",  help="Upload a CSV file to visualize its data. As of now only CSV files are supported.")
# if uploaded_files is not None:    #for multiple file upload
#     for uploaded_file in uploaded_files:
#         df = pd.read_csv(uploaded_file)
#         # df = dataframe = pd.read_csv(uploaded_files)
#         st.dataframe(df) # Display the uploaded DataFrame for debugging

if "plot" not in st.session_state:
    st.session_state.plot = None

if "stats" not in st.session_state:
    st.session_state.stats = None

if "warning" not in st.session_state:
    st.session_state.warning = None

uploaded_file = st.file_uploader("Drag and drop your CSV file here", type=["csv"], key="file_uploader", on_change=change_state, help="Upload a CSV file to visualize its data. As of now only CSV files are supported.")
warning_spot = st.empty()

col1, col2 = st.columns([3.5,2.5]) # 80% plot, 20% info
if uploaded_file is not None:
    df = dataframe = pd.read_csv(uploaded_file)
    st.sidebar.subheader("Select Columns to Plot and Plot Type")
    column_for_X_axis = st.sidebar.selectbox("Select Column for X-axis", df.columns, index=None, key="x_axis_select")
    column_for_Y_axis = st.sidebar.selectbox("Select Column for Y-axis", df.columns, index=None, key="y_axis_select")
    plot_type = st.sidebar.selectbox("Select Plot Type", ["Scatter Plot", "Line Plot", "Bar Plot"], index=None)

    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist() # Identify categorical columns for special handling in scatter plot
       
    if column_for_X_axis and column_for_Y_axis and plot_type:
        color_by_column = st.sidebar.selectbox("Color by Column", df.columns, index=None, key="color_by_select")
        
        if st.sidebar.button("Generate Plot", icon="📊", width="stretch"):
            # Reset the warning every time a new plot is requested
            st.session_state.warning = None
            if plot_type == "Scatter Plot":
                if column_for_X_axis in categorical_cols or column_for_Y_axis in categorical_cols:
                    st.session_state.warning = "Scatter plot may not be suitable for categorical data. Consider using a different plot type."
                    fig = px.strip(df, x=column_for_X_axis, y=column_for_Y_axis, color=color_by_column)
                else:
                    fig = px.scatter(df, x=column_for_X_axis, y=column_for_Y_axis, color=color_by_column)
                               
                st.session_state.plot = fig
            
            if color_by_column: # If a color grouping column is selected, calculate and store the value counts for that column in session state to display in the info column
                st.session_state.stats = df[color_by_column].value_counts()
            else:
                st.session_state.stats = "No color grouping selected. Stats not available."
    
    if st.session_state.warning:
        warning_spot.warning(st.session_state.warning)
                
    if "plot" in st.session_state and st.session_state.plot is not None:
        with col1:
            st.plotly_chart(st.session_state.plot, width="stretch")
        with col2:
            st.subheader("Data Summary", width="content")
            if isinstance(st.session_state.stats, str):
                st.info(st.session_state.stats)
            else:
                st.dataframe(df.describe(include='all').T.astype(str).replace('nan', '-'))
            
                # elif plot_type == "Line Plot":
        #     plt.figure(figsize=(10, 6))
        #     plt.plot(df[column_for_X_axis], df[column_for_Y_axis])
        #     plt.xlabel(column_for_X_axis)
        #     plt.ylabel(column_for_Y_axis)
        #     plt.title(f"Line Plot of {column_for_Y_axis} vs {column_for_X_axis}")
        #     st.pyplot(plt)

        # elif plot_type == "Bar Plot":
        #     plt.figure(figsize=(10, 6))
        #     plt.bar(df[column_for_X_axis], df[column_for_Y_axis])
        #     plt.xlabel(column_for_X_axis)
        #     plt.ylabel(column_for_Y_axis)
        #     plt.title(f"Bar Plot of {column_for_Y_axis} vs {column_for_X_axis}")
        #     st.pyplot(plt)
            
st.write(st.session_state)
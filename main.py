from genericpath import exists

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

def change_state():
    st.session_state.plot = None
    st.session_state.column_data = None
    st.session_state.ui_alert_message = None

            
st.set_page_config(page_title="EZ Plots", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)    
st.title("EZ_Plots: Your Data's Best Friend for Quick and Easy Visualization")
st.sidebar.title("Toolbar")
date_column = None
# uploaded_files = st.file_uploader("Drag and drop your CSV file here", accept_multiple_files=True, type=["csv"], key="file_uploader",  help="Upload a CSV file to visualize its data. As of now only CSV files are supported.")
# if uploaded_files is not None:    #for multiple file upload
#     for uploaded_file in uploaded_files:
#         df = pd.read_csv(uploaded_file)
#         # df = dataframe = pd.read_csv(uploaded_files)
#         st.dataframe(df) # Display the uploaded DataFrame for debugging

if "plot" not in st.session_state:
    st.session_state.plot = None

if "ui_alert_message" not in st.session_state:
    st.session_state.ui_alert_message = None
    
if "column_data" not in st.session_state:
    st.session_state.column_data = None
    
if "info_msg" not in st.session_state:
    st.session_state.info_msg = None

if "top_trait" not in st.session_state:    
    st.session_state.top_trait = None
        
uploaded_file = st.file_uploader("Drag and drop your CSV file here", type=["csv"], key="file_uploader", on_change=change_state, help="Upload a CSV file to visualize its data. As of now only CSV files are supported.")
warning_spot = st.empty() # Placeholder for displaying warnings related to plot suitability based on data types. This allows us to show warnings without disrupting the layout of the plot and info columns.

col1, col2 = st.columns([0.6, 0.4]) 
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='latin-1')
    st.sidebar.subheader("Select Columns to Plot and Plot Type")
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f"🕵️ Detective is checking column: {col}")
            temp_date = pd.to_datetime(df[col], errors='coerce',format='mixed') # Attempt to convert to datetime, coercing errors to NaT. The 'format' parameter is set to 'mixed' to allow for multiple date formats within the same column, which is a common scenario in real-world datasets. This way, we can still identify and convert valid date entries while gracefully handling any non-date entries without causing the entire conversion to fail.
            if temp_date.notnull().sum() > (0.8 * len(df)):
                print("gets in here")
                df[col] = temp_date.dt.year # Convert to Year
                df = df.dropna(subset=[col]) # Drop the "Bad" rows immediately
                df[col] = df[col].astype(int) # Safe to turn into an official integer
                date_column = df[col].name
    
    column_for_X_axis = st.sidebar.selectbox("Select Column for X-axis", df.columns, index=None, key="x_axis_select")
    
    temp_num_cols = []
    if date_column:                  
        temp_num_cols = [col for col in df.select_dtypes(include=['number']).columns.tolist() if col != date_column] # Exclude the date column from the list of numeric columns to prevent it from being selected as the Y-axis in the plot, which could lead to misleading visualizations. By doing this, we ensure that users are only able to select appropriate numeric columns for the Y-axis, while still allowing the date column to be used as the X-axis for time series visualizations.
    
    if not temp_num_cols:
        temp_num_cols = [col for col in df.columns if col != column_for_X_axis] # If no numeric columns are available, allow all columns except the X-axis column to be selected for the Y-axis. This provides flexibility for users to still create visualizations even when their dataset doesn't contain numeric columns, while also preventing them from selecting the same column for both axes which would lead to an uninformative plot.
    
    column_for_Y_axis = st.sidebar.selectbox("Select Column for Y-axis", temp_num_cols, index=None, key="y_axis_select")
    plot_type = st.sidebar.selectbox("Select Plot Type", ["Scatter Plot", "Line Plot", "Bar Plot"], index=None)

    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist() # Identify categorical columns for special handling in scatter plot
       
    if column_for_X_axis and column_for_Y_axis and plot_type:
        color_by_col_options = [col for col in df.columns if col != column_for_X_axis and col != column_for_Y_axis] # Exclude the X-axis and Y-axis columns from the color grouping options to prevent crashing when df.groupby([column_for_X_axis, color_by_column]) is used for line plot, since grouping by these columns doesn't make sense and can lead to errors or misleading visualizations. By excluding these columns from the color grouping options, we guide users towards making more meaningful selections for their visualizations.
        color_by_column = st.sidebar.selectbox("Color by Column", color_by_col_options, index=None, key="color_by_select")
        
        if plot_type == "Line Plot" and color_by_column:
            selected_items = st.sidebar.multiselect(
                    f"Select {color_by_column} to Compare", 
                    options=df[color_by_column].fillna("Missing").unique(), # need to work on the nan errors i get when there are nulls in the color by column. 
                    default=df[color_by_column].fillna("Missing").unique()[:5] # Default to the first 5
                )
            if not selected_items:
                print("gets in not selected items warning")
                warning_spot.warning("Please select at least one category to compare in the line plot.")
                
        if st.sidebar.button("Generate Plot", icon="📊", width="stretch"):
            # Reset the warning every time a new plot is requested
            st.session_state.ui_alert_message = None
            if plot_type == "Scatter Plot":
                if column_for_X_axis in categorical_cols or column_for_Y_axis in categorical_cols:
                    st.session_state.ui_alert_message = "Scatter plot may not be suitable for categorical data. Consider using a different plot type."
                    fig = px.strip(df, x=column_for_X_axis, y=column_for_Y_axis, color=color_by_column) # Using strip plot as an alternative to scatter plot for categorical data to provide a better visualization of the distribution of data points across categories. This allows users to still visualize relationships between variables even when they are categorical, while also addressing the issue of overplotting that can occur with scatter plots when dealing with categorical data.
                else:
                    fig = px.scatter(df, x=column_for_X_axis, y=column_for_Y_axis, color=color_by_column)
            elif plot_type == "Line Plot":
                group_cols = [column_for_X_axis]
                if color_by_column:
                    group_cols.append(color_by_column)
                df_grouped = df.groupby(group_cols) # Group the DataFrame by the X-axis column and the color grouping column (if selected) to prepare for aggregation. This allows us to calculate summary statistics for each group defined by the unique combinations of the X-axis values and the color grouping categories, which is essential for creating meaningful line plots that show trends over the X-axis while comparing different groups based on the color grouping.
                if pd.api.types.is_numeric_dtype(df[column_for_Y_axis]):
                    df_grouped = df_grouped[column_for_Y_axis].mean().reset_index() # For numeric Y-axis, calculate the mean for each group to create a meaningful line plot that shows trends over the X-axis while comparing different categories based on the color grouping. This allows users to visualize how the average value of the Y-axis variable changes across the X-axis for different groups defined by the color grouping column.
                else:
                    df_grouped = df_grouped[column_for_Y_axis].count().reset_index() # For non-numeric Y-axis, calculate the count for each group to create a line plot that shows the frequency of occurrences for each category across the X-axis while comparing different groups based on the color grouping. This provides insights into the distribution of categorical data across the X-axis and how it varies between different groups defined by the color grouping column.
                df_grouped = df_grouped.sort_values(by=column_for_X_axis)
                if color_by_column:
                    df_final = df_grouped[df_grouped[color_by_column].isin(selected_items)] 
                else:
                    df_final = df_grouped
                print(df_grouped)

                fig = px.line(df_final, x=column_for_X_axis, y=column_for_Y_axis, color=color_by_column)

            else:
                pass
            
            if color_by_column: # If a color grouping column is selected, calculate and store the value counts for that column in session state to display in the info column
                summary_df = df[color_by_column].value_counts().to_frame()
                summary_df = summary_df.rename(columns={"count":"Count"})
                summary_df["Percentage %"] = (summary_df["Count"]/summary_df["Count"].sum() * 100)
                max_value_name = summary_df["Count"].idxmax()
                max_value_percent = summary_df["Percentage %"].max()
                st.session_state.top_trait = f"In this dataset, {max_value_name} accounts for {max_value_percent:.1f}% of the distribution."
                st.session_state.column_data = summary_df
                st.session_state.info_msg = None
            else:
                st.session_state.info_msg = "No color grouping selected. Value counts not available."
                st.session_state.column_data = None 
            st.session_state.plot = fig                
            

    if st.session_state.ui_alert_message:
        warning_spot.warning(st.session_state.ui_alert_message)
    
    if "plot" in st.session_state and st.session_state.plot is not None:
        with col1:
            st.subheader("Plot", width="content")
            st.plotly_chart(st.session_state.plot, width="stretch")
        with col2:
            st.subheader("Data Summary", width="content")
            toggle_button = st.toggle("Raw Data", key="show_stats_toggle")
            if toggle_button:
                    st.dataframe(df.describe(include='all').T.astype(str).replace('nan', '-'))
            else:
                if st.session_state.column_data is not None: # If a color grouping column is selected, display the value counts for that column in the info column. This provides users with insights into the distribution of categories in the selected color grouping column, which can help them interpret the plot more effectively.
                    st.dataframe(
                                st.session_state.column_data,
                                column_config={
                                    "Percentage %": st.column_config.NumberColumn(
                                        "Share",
                                        format="%.1f%%"  # This is the "Magic Code" for 1 decimal + % sign
                                    )
                                }
                                )
                    st.info(st.session_state.top_trait,icon="ℹ️")
                else:
                    st.info(st.session_state.info_msg)
            
st.write(st.session_state)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def change_state():
    st.session_state.plot = None
    
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

uploaded_file = st.file_uploader("Drag and drop your CSV file here", type=["csv"], key="file_uploader", on_change=change_state, help="Upload a CSV file to visualize its data. As of now only CSV files are supported.")
if uploaded_file is not None:
    df = dataframe = pd.read_csv(uploaded_file)
    st.sidebar.subheader("Select Columns to Plot and Plot Type")
    column_for_X_axis = st.sidebar.selectbox("Select Column for X-axis", df.columns, index=None, key="x_axis_select")
    column_for_Y_axis = st.sidebar.selectbox("Select Column for Y-axis", df.columns, index=None, key="y_axis_select")
    plot_type = st.sidebar.selectbox("Select Plot Type", ["Scatter Plot", "Line Plot", "Bar Plot"], index=None)

    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist() # Identify categorical columns for special handling in scatter plot
   
    
    if column_for_X_axis and column_for_Y_axis and plot_type:
        st.write(f"You selected X-axis: {column_for_X_axis}, Y-axis: {column_for_Y_axis}, Plot Type: {plot_type}")
        color_by_column = st.sidebar.selectbox("Color by Column", df.columns, index=None, key="color_by_select")
        color_code = None
        if color_by_column: # If a color by column is selected, determine if it's categorical or numerical and assign appropriate color codes for plotting.
            if color_by_column in categorical_cols:
                color_code = df[color_by_column].astype('category').cat.codes 
            else:
                color_code = df[color_by_column]         
        
        if st.sidebar.button("Generate Plot", icon="📊", width="stretch"):
            if plot_type == "Scatter Plot":
                fig, ax = plt.subplots()
                if column_for_X_axis in categorical_cols or column_for_Y_axis in categorical_cols:
                    cat_x = df[column_for_X_axis].astype('category')
                    cat_y = df[column_for_Y_axis].astype('category')
                    
                    st.warning("Scatter plot may not be suitable for categorical data. Consider using a different plot type.")
                    x_data = cat_x.cat.codes #Takes your column of words, assigns a number to each unique word, and returns a list of those numbers.
                    y_data = cat_y.cat.codes #Takes your column of words, assigns a number to each unique word, and returns a list of those numbers.
                    jitter_x = np.random.uniform(-0.2,0.2,size=len(df)) # Adds a small random value to each point to prevent overlap in the scatter plot, making it easier to visualize the distribution of categorical data.
                    jitter_y = np.random.uniform(-0.2,0.2,size=len(df))
                    scatter = ax.scatter(x_data + jitter_x, y_data + jitter_y, alpha=0.1 , c=color_code) # Creates a scatter plot with jittered x and y data to visualize categorical variables, with points having low opacity (alpha=0.1) to show density.
                    
                    ax.set_xticks(range(len(cat_x.cat.categories))) # Sets the x-axis ticks to correspond to the unique categories in the selected X-axis column, ensuring that each category is represented on the plot.
                    ax.set_xticklabels(cat_x.cat.categories, ha="right") # Sets the x-axis tick labels to the original category names from the selected X-axis column, aligning them to the right for better readability.
                    ax.set_yticks(range(len(cat_y.cat.categories)))
                    ax.set_yticklabels(cat_y.cat.categories, ha="right")
                    
                #to be fixed-->    ax.legend([], loc="upper right", title=f"{color_by_column}") # Adds a legend to the plot based on the color coding of the points, showing the categories or values of the selected color by column.
                    
                else:      
                    ax.scatter(df[column_for_X_axis], df[column_for_Y_axis],alpha=0.1, c=color_code) # Creates a scatter plot using the selected X and Y columns from the DataFrame, with points having low opacity (alpha=0.1) to show density, and colored based on the selected color column.
                
                ax.set_xlabel(f'{column_for_X_axis}')
                ax.set_ylabel(f'{column_for_Y_axis}')
                ax.set_title(f"Scatter Plot of {column_for_Y_axis} vs {column_for_X_axis}")
                st.session_state.plot = fig

    
    if st.session_state.plot is not None:
        st.pyplot(st.session_state.plot)


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
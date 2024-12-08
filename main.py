import pandas as pd
import streamlit as st
import plotly.express as px

#Set page configuration
st.set_page_config(layout="wide")
# read data
work_df = pd.read_csv('data/Impact_of_Remote_Work_on_Mental_Health.csv')

# Cache data for faster Data Retrieval
st.cache_data(show_spinner="Loading..")
def load_data(file):
    work_df = pd.read_csv(file)
    return work_df
# Sidebar for region selection
st.sidebar.title("Filter by Region")
regions = work_df['Region'].dropna().unique()
selected_region = st.sidebar.selectbox("Select a Region", options=regions, index=0)

# Filter data based on selected region
filtered_data = work_df[work_df['Region'] == selected_region]

# Main tabs
st.title("Impact of Remote Work on Mental Health")
tab1, tab2, tab3 = st.tabs(["Overview", "Stress Analysis", "Industry Insights"])

# Tab 1: Overview
with tab1:
    st.markdown(
        """ Remote work became more prevalent since the covid-19 pandemic, which proved to be a blessing for many employees. According to a study from Owl Labs and Global Workplace Analytics, 62% of employees feel more proactive when working remotely, and 52% said they’d trade a slight reduction in pay for the option to work from home. As working from home allows a better work-life balance. This also leads to higher job satisfaction and a greater likelihood that they’ll stay with the company. Now since the pandemic era is long gone and companies have started bring in 5 day in office mandate, should companies really do that or should they give a hybrid/remote option, lets find out!"""
    )
    st.header(f"Overview for {selected_region}")
# Bar graph: Job Role divided by Gender
    st.subheader("Job Role Distribution by Gender")
    if not filtered_data[['Job_Role', 'Gender']].isna().all().any():
        gender_job_data = filtered_data[['Job_Role', 'Gender']].dropna()

        # Count the occurrences of each gender per job role
        job_role_gender_counts = gender_job_data.groupby(['Job_Role', 'Gender']).size().reset_index(name='Count')

        # Bar graph using Plotly
        fig = px.bar(
            job_role_gender_counts,
            x='Job_Role',
            y='Count',
            color='Gender',
            barmode='group',
            labels={'Count': 'Number of Employees', 'Job_Role': 'Job Role'},
            height=500,
        )
        # Update layout for better visuals
        fig.update_layout(
            xaxis=dict(title="Job Role", tickangle=45),
            yaxis_title="Number of Employees",
            legend_title="Gender",
            bargap=0.2,
        )
        # Display the Plotly chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No valid data available for Job Role and Gender distribution.")

    # Line Graph: Age vs. Average Hours Worked Per Week
    st.subheader("Age vs. Average Hours Worked Per Week")
    if 'Age' in filtered_data and 'Hours_Worked_Per_Week' in filtered_data:
        # Ensure numeric data
        filtered_data['Age'] = pd.to_numeric(filtered_data['Age'], errors='coerce')
        filtered_data['Hours_Worked_Per_Week'] = pd.to_numeric(filtered_data['Hours_Worked_Per_Week'], errors='coerce')

        # Drop rows with missing values
        age_hours_data = filtered_data.dropna(subset=['Age', 'Hours_Worked_Per_Week'])

        if not age_hours_data.empty:
            # Calculate the average hours worked per week for each age
            avg_hours_per_age = age_hours_data.groupby('Age', as_index=False)['Hours_Worked_Per_Week'].mean()

            # Interactive line graph
            fig = px.line(
                avg_hours_per_age,
                x='Age',
                y='Hours_Worked_Per_Week',
                labels={'Age': 'Age', 'HHours_Worked_Per_Week': 'Average Hours Worked Per Week'},
                markers=True,
            )
            # Display the graph
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid data available for Age and Hours Worked Per Week.")
    else:
        st.warning("Required columns 'Age' and 'Hours Worked Per Week' are missing.")
# Tab2: Stress Analysis        
with tab2:
    st.header(f"Industry-Wide Insights for {selected_region}")
    # Dropdown for job role
    st.subheader("Filter by Job Role and Work Location")
    job_roles = filtered_data['Job_Role'].dropna().unique()
    selected_job_role = st.selectbox("Select a Job Role", options=job_roles)

    # Dropdown for work location
    work_locations = filtered_data['Work_Location'].dropna().unique()
    selected_work_location = st.selectbox("Select a Work Location", options=work_locations)

    # Filter data by the selected job role and work location
    role_data = filtered_data[
        (filtered_data['Job_Role'] == selected_job_role) &
        (filtered_data['Work_Location'] == selected_work_location)
    ].copy()

    if not role_data.empty:
        # Create columns for Productivity and Stress graphs
        col1, col2 = st.columns(2)

        # Column 1: Productivity Change Graph
        with col1:
            st.subheader("Productivity Change Distribution")
            productivity_counts = role_data.groupby(['Productivity_Change']).size().reset_index(name='Count')
            total_productivity = productivity_counts['Count'].sum()
            productivity_counts['Percentage'] = (productivity_counts['Count'] / total_productivity * 100).round(1)

            # Create a bar chart using Plotly
            fig_productivity_distribution = px.bar(
                productivity_counts,
                x='Productivity_Change',
                y='Count',
                color='Productivity_Change',
                barmode='group',
                labels={'Productivity_Change': 'Productivity Change', 'Count': 'Number of People'},
                height=400,
            )

            # Add percentage to the tooltip
            fig_productivity_distribution.update_traces(
                customdata=productivity_counts[['Percentage']],
                hovertemplate='Productivity Change: %{x}<br>Count: %{y}<br>Percentage: %{customdata[0]}%',
            )

            # Display the chart
            st.plotly_chart(fig_productivity_distribution, use_container_width=True)

        # Column 2: Stress Level Graph
        with col2:
            st.subheader("Stress Level Distribution")
            stress_counts = role_data.groupby(['Stress_Level']).size().reset_index(name='Count')
            total_stress = stress_counts['Count'].sum()
            stress_counts['Percentage'] = (stress_counts['Count'] / total_stress * 100).round(1)

            # Create a bar chart using Plotly
            fig_stress_distribution = px.bar(
                stress_counts,
                x='Stress_Level',
                y='Count',
                color='Stress_Level',
                barmode='group',
                labels={'Stress_Level': 'Stress Level', 'Count': 'Number of People'},
                height=400,
            )
            # Add percentage to the tooltip
            fig_stress_distribution.update_traces(
                customdata=stress_counts[['Percentage']],
                hovertemplate='Stress Level: %{x}<br>Count: %{y}<br>Percentage: %{customdata[0]}%',
            )
            # Display the chart
            st.plotly_chart(fig_stress_distribution, use_container_width=True)

        # Employee Satisfaction Breakdown in the center
        st.subheader("Employee Satisfaction Breakdown")
        satisfaction_counts = role_data.groupby('Satisfaction_with_Remote_Work').size().reset_index(name='Count')

        fig_satisfaction_pie = px.pie(
            satisfaction_counts,
            values='Count',
            names='Satisfaction_with_Remote_Work',
            labels={'Satisfaction_with_Remote_Work': 'Satisfaction Level'},
            hole=0.4,  # For a donut-style pie chart
        )

        # Display the pie chart in the center
        st.plotly_chart(fig_satisfaction_pie, use_container_width=True)
    else:
        st.warning(f"No data available for the selected job role ({selected_job_role}) and work location ({selected_work_location}).")
# Tab 3: Job Satisfaction
with tab3:
    st.header(f"Industry-Wide Insights for {selected_region}")

    # Filter data by the selected region
    region_data = filtered_data[filtered_data['Region'] == selected_region].copy()

    # Dropdown for industry selection
    industries = region_data['Industry'].dropna().unique()
    selected_industry = st.selectbox("Select an Industry", options=industries)

    # Filter data by the selected industry
    industry_data = region_data[region_data['Industry'] == selected_industry].copy()

    if not industry_data.empty:
        # Columns for Stress Level and Work Satisfaction graphs
        col1, col2 = st.columns(2)

        # Column 1: Stress Level Vertical Bar Graph with Percentages
        with col1:
            st.subheader("Stress Level Distribution")
            if 'Stress_Level' in industry_data.columns:
                # Calculate counts and percentages
                stress_counts = industry_data.groupby('Stress_Level').size().reset_index(name='Count')
                total_stress = stress_counts['Count'].sum()
                stress_counts['Percentage'] = (stress_counts['Count'] / total_stress * 100).round(1)

                #Bar Chart with Percentages
                fig_stress_distribution = px.bar(
                    stress_counts,
                    x='Stress_Level',
                    y='Count',
                    color='Stress_Level',
                    labels={'Stress_Level': 'Stress Level', 'Count': 'Number of People'},
                    text='Percentage', 
                )
                # Update layout for display
                fig_stress_distribution.update_traces(
                    texttemplate='%{text}%', textposition='inside', textfont_size=18
                )
                fig_stress_distribution.update_layout(
                    bargap=0.2,
                    width=600,  
                    height=500,  
                    font=dict(size=16), 
                )
                # Display the chart
                st.plotly_chart(fig_stress_distribution, use_container_width=False)
            else:
                st.warning("Stress Level data not available.")

        # Column 2: Work Satisfaction Bar Graph 
        with col2:
            st.subheader("Work Satisfaction Distribution")
            if 'Satisfaction_with_Remote_Work' in industry_data.columns:
                # Calculate counts and percentages
                satisfaction_counts = (
                    industry_data.groupby('Satisfaction_with_Remote_Work')
                    .size()
                    .reset_index(name='Count')
                )
                total_satisfaction = satisfaction_counts['Count'].sum()
                satisfaction_counts['Percentage'] = (satisfaction_counts['Count'] / total_satisfaction * 100).round(1)

                #  Bar Chart with Percentages
                fig_satisfaction_distribution = px.bar(
                    satisfaction_counts,
                    x='Satisfaction_with_Remote_Work',
                    y='Count',
                    color='Satisfaction_with_Remote_Work',
                    labels={
                        'Satisfaction_with_Remote_Work': 'Satisfaction Level',
                        'Count': 'Number of People',
                    },
                    text='Percentage', 
                )

                # Update layout for display
                fig_satisfaction_distribution.update_traces(
                    texttemplate='%{text}%', textposition='inside', textfont_size=18
                )
                fig_satisfaction_distribution.update_layout(
                    bargap=0.2,
                    width=600,  
                    height=500, 
                    font=dict(size=16),
                )

                # Display the chart
                st.plotly_chart(fig_satisfaction_distribution, use_container_width=False)
            else:
                st.warning("Work Satisfaction data not available.")
    else:
        st.warning(f"No data available for the selected industry ({selected_industry}) in region ({selected_region}).")


    # Add data source link
    st.markdown(
        """
        ### Data Sources
        - [Remote Work & Mental Health](https://www.kaggle.com/datasets/waqi786/remote-work-and-mental-health/data)
        - [How Remote Work Can Impact Employees' Mental Health](https://www.forbes.com/councils/forbeshumanresourcescouncil/2023/07/03/how-remote-work-can-impact-employees-mental-health/)
        """
    )

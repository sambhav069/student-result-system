# app.py - Streamlit web application
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import StudentDatabase
import sqlite3

# Configure Streamlit page
# This sets the title, icon, and layout of your Streamlit app.

st.set_page_config(
    page_title="Student Result Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
# This initializes your database only once to avoid reloading on every interaction.
@st.cache_resource
def init_database():
    return StudentDatabase()

db = init_database()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #667eea;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-message {
        padding: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-message {
        padding: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
    .grade-a { background-color: #28a745; color: white; padding: 2px 8px; border-radius: 4px; }
    .grade-b { background-color: #17a2b8; color: white; padding: 2px 8px; border-radius: 4px; }
    .grade-c { background-color: #ffc107; color: black; padding: 2px 8px; border-radius: 4px; }
    .grade-d { background-color: #fd7e14; color: white; padding: 2px 8px; border-radius: 4px; }
    .grade-f { background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("<h1 class='main-header'>🎓 Student Result Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Manage students, subjects, and results efficiently</p>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["📊 Dashboard", "👥 Students", "📚 Subjects", "📝 Results", "📋 Reports"]
)

# Dashboard Page
if page == "📊 Dashboard":
    st.header("📊 Dashboard")
    
    # Get dashboard statistics
    stats = db.get_dashboard_stats()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", stats["total_students"])
    
    with col2:
        st.metric("Total Subjects", stats["total_subjects"])
    
    with col3:
        st.metric("Average Marks", f"{stats['avg_marks']}")
    
    with col4:
        st.metric("Pass Rate", f"{stats['pass_rate']}%")
    
    # Charts
    if stats["total_students"] > 0:
        st.subheader("📈 Analytics")
        
        # Get all results for visualization
        results_df = db.get_all_results()
        
        if not results_df.empty and results_df['marks'].notna().any():
            col1, col2 = st.columns(2)
            
            with col1:
                # Subject-wise average marks
                subject_avg = results_df.groupby('subject_name')['marks'].mean().reset_index()
                subject_avg.columns = ['Subject', 'Average Marks']
                
                fig_bar = px.bar(
                    subject_avg, 
                    x='Subject', 
                    y='Average Marks',
                    title='Subject-wise Average Marks',
                    color='Average Marks',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Grade distribution
                results_df['percentage'] = (results_df['marks'] / results_df['max_marks']) * 100
                results_df['grade'] = results_df['percentage'].apply(lambda x: db.get_grade(x) if pd.notna(x) else 'N/A')
                
                grade_counts = results_df['grade'].value_counts()
                
                fig_pie = px.pie(
                    values=grade_counts.values,
                    names=grade_counts.index,
                    title='Grade Distribution'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

# Students Page
elif page == "👥 Students":
    st.header("👥 Student Management")
    
    tab1, tab2 = st.tabs(["Add Student", "Manage Students"])
    
    with tab1:
        st.subheader("Add New Student")
        
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_id = st.text_input("Student ID*", placeholder="e.g., S001")
                student_name = st.text_input("Student Name*", placeholder="e.g., John Doe")
            
            with col2:
                student_class = st.text_input("Class*", placeholder="e.g., 10th Grade")
            
            submitted = st.form_submit_button("Add Student", use_container_width=True)
            
            if submitted:
                if student_id and student_name and student_class:
                    success = db.add_student(student_id, student_name, student_class)
                    if success:
                        st.success(f"Student {student_name} added successfully!")
                        st.rerun()
                    else:
                        st.error("Student ID already exists!")
                else:
                    st.error("Please fill all required fields!")
    
    with tab2:
        st.subheader("Current Students")
        
        students = db.get_all_students()
        
        if students:
            # Display students in a nice format
            for student in students:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{student['name']}**")
                    
                    with col2:
                        st.write(f"ID: {student['id']}")
                    
                    with col3:
                        st.write(f"Class: {student['class']}")
                    
                    with col4:
                        if st.button("Delete", key=f"del_student_{student['id']}", type="secondary"):
                            if db.delete_student(student['id']):
                                st.success("Student deleted!")
                                st.rerun()
                    
                    st.divider()
            
            # Clear all students button
            if st.button("Clear All Students", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_clear_students', False):
                    db.clear_all_students()
                    st.success("All students cleared!")
                    st.session_state['confirm_clear_students'] = False
                    st.rerun()
                else:
                    st.session_state['confirm_clear_students'] = True
                    st.warning("Click again to confirm deletion of all students!")
        else:
            st.info("No students found. Add some students to get started!")

# Subjects Page
elif page == "📚 Subjects":
    st.header("📚 Subject Management")
    
    tab1, tab2 = st.tabs(["Add Subject", "Manage Subjects"])
    
    with tab1:
        st.subheader("Add New Subject")
        
        with st.form("add_subject_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                subject_name = st.text_input("Subject Name*", placeholder="e.g., Mathematics")
            
            with col2:
                max_marks = st.number_input("Maximum Marks*", min_value=1, max_value=1000, value=100)
            
            submitted = st.form_submit_button("Add Subject", use_container_width=True)
            
            if submitted:
                if subject_name:
                    success = db.add_subject(subject_name, max_marks)
                    if success:
                        st.success(f"Subject {subject_name} added successfully!")
                        st.rerun()
                    else:
                        st.error("Subject already exists!")
                else:
                    st.error("Please enter subject name!")
    
    with tab2:
        st.subheader("Current Subjects")
        
        subjects = db.get_all_subjects()
        
        if subjects:
            # Display subjects in a table
            subjects_df = pd.DataFrame(subjects)
            subjects_df.columns = ['Subject Name', 'Maximum Marks']
            
            # Add delete buttons
            for i, subject in enumerate(subjects):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{subject['name']}**")
                
                with col2:
                    st.write(f"Max Marks: {subject['max_marks']}")
                
                with col3:
                    if st.button("Delete", key=f"del_subject_{subject['name']}", type="secondary"):
                        if db.delete_subject(subject['name']):
                            st.success("Subject deleted!")
                            st.rerun()
                
                st.divider()
            
            # Clear all subjects button
            if st.button("Clear All Subjects", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_clear_subjects', False):
                    db.clear_all_subjects()
                    st.success("All subjects cleared!")
                    st.session_state['confirm_clear_subjects'] = False
                    st.rerun()
                else:
                    st.session_state['confirm_clear_subjects'] = True
                    st.warning("Click again to confirm deletion of all subjects!")
        else:
            st.info("No subjects found. Add some subjects to get started!")

# Results Page
elif page == "📝 Results":
    st.header("📝 Results Management")
    
    students = db.get_all_students()
    subjects = db.get_all_subjects()
    
    if not students:
        st.warning("No students found. Please add students first!")
    elif not subjects:
        st.warning("No subjects found. Please add subjects first!")
    else:
        # Student selection
        student_options = {f"{s['name']} ({s['id']})": s['id'] for s in students}
        selected_student_display = st.selectbox("Select Student", list(student_options.keys()))
        selected_student_id = student_options[selected_student_display]
        
        if selected_student_id:
            st.subheader(f"Enter Marks for {selected_student_display}")
            
            # Get current results for the student
            current_results = db.get_student_results(selected_student_id)
            
            with st.form("marks_form"):
                marks_data = {}
                
                # Create input fields for each subject
                cols = st.columns(2)
                for i, subject in enumerate(subjects):
                    col = cols[i % 2]
                    with col:
                        current_mark = current_results.get(subject['name'], 0)
                        mark = st.number_input(
                            f"{subject['name']} (Max: {subject['max_marks']})",
                            min_value=0,
                            max_value=subject['max_marks'],
                            value=current_mark,
                            key=f"mark_{subject['name']}"
                        )
                        marks_data[subject['name']] = mark
                
                submitted = st.form_submit_button("Save Marks", use_container_width=True)
                
                if submitted:
                    success_count = 0
                    for subject_name, marks in marks_data.items():
                        if db.save_marks(selected_student_id, subject_name, marks):
                            success_count += 1
                    
                    if success_count == len(marks_data):
                        st.success("All marks saved successfully!")
                        st.rerun()
                    else:
                        st.error("Some marks could not be saved!")
            
            # Display current results
            if current_results:
                st.subheader("Current Results")
                results_display = []
                
                for subject in subjects:
                    if subject['name'] in current_results:
                        marks = current_results[subject['name']]
                        percentage = (marks / subject['max_marks']) * 100
                        grade = db.get_grade(percentage)
                        
                        results_display.append({
                            'Subject': subject['name'],
                            'Marks': f"{marks}/{subject['max_marks']}",
                            'Percentage': f"{percentage:.1f}%",
                            'Grade': grade
                        })
                
                if results_display:
                    df = pd.DataFrame(results_display)
                    st.dataframe(df, use_container_width=True, hide_index=True)

# Reports Page
elif page == "📋 Reports":
    st.header("📋 Reports")
    
    students = db.get_all_students()
    
    if not students:
        st.warning("No students found. Please add students first!")
    else:
        # Student selection for report
        student_options = {f"{s['name']} ({s['id']})": s['id'] for s in students}
        selected_student_display = st.selectbox("Select Student for Report", list(student_options.keys()))
        selected_student_id = student_options[selected_student_display]
        
        if st.button("Generate Report", use_container_width=True):
            report = db.generate_student_report(selected_student_id)
            
            if report:
                # Student info
                st.subheader("📋 Report Card")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Name:** {report['student']['name']}")
                with col2:
                    st.write(f"**ID:** {report['student']['id']}")
                with col3:
                    st.write(f"**Class:** {report['student']['class']}")
                
                st.divider()
                
                # Results table
                if report['results']:
                    results_df = pd.DataFrame(report['results'])
                    results_df.columns = ['Subject', 'Marks', 'Max Marks', 'Percentage', 'Grade']
                    
                    # Style the dataframe
                    def style_grades(val):
                        if val == 'A':
                            return 'background-color: #28a745; color: white'
                        elif val == 'B':
                            return 'background-color: #17a2b8; color: white'
                        elif val == 'C':
                            return 'background-color: #ffc107; color: black'
                        elif val == 'D':
                            return 'background-color: #fd7e14; color: white'
                        elif val == 'F':
                            return 'background-color: #dc3545; color: white'
                        return ''
                    
                    styled_df = results_df.style.applymap(style_grades, subset=['Grade'])
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    # Overall summary
                    st.subheader("📊 Overall Performance")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Marks", f"{report['summary']['total_marks']}/{report['summary']['total_max_marks']}")
                    
                    with col2:
                        st.metric("Overall Percentage", f"{report['summary']['overall_percentage']}%")
                    
                    with col3:
                        st.metric("Overall Grade", report['summary']['overall_grade'])
                    
                    with col4:
                        status = "PASS" if report['summary']['overall_percentage'] >= 60 else "FAIL"
                        st.metric("Status", status)
                    
                    # Performance chart
                    fig = px.bar(
                        results_df,
                        x='Subject',
                        y='Percentage',
                        title='Subject-wise Performance',
                        color='Percentage',
                        color_continuous_scale='RdYlGn'
                    )
                    fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Pass Line (60%)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.info("No results found for this student.")
            else:
                st.error("Could not generate report. Student not found.")
        
        # All students summary
        st.subheader("📊 All Students Summary")
        
        if st.button("Show All Students Performance"):
            all_results = db.get_all_results()
            
            if not all_results.empty and all_results['marks'].notna().any():
                # Calculate student-wise performance
                student_performance = []
                
                subjects = db.get_all_subjects()

                for student in students:
                    student_results = db.get_student_results(student['id'])
                    if student_results:
                        total_marks = sum(student_results.values())
                        subjects_taken = len(student_results)
                        avg_marks = total_marks / subjects_taken if subjects_taken > 0 else 0
                        
                        # Get max marks for percentage calculation
                        total_max_marks = 0
                        for subject_name, marks in student_results.items():
                            subject_info = next((s for s in subjects if s['name'] == subject_name), None)
                            if subject_info:
                                total_max_marks += subject_info['max_marks']
                        
                        percentage = (total_marks / total_max_marks * 100) if total_max_marks > 0 else 0
                        grade = db.get_grade(percentage)
                        status = "PASS" if percentage >= 60 else "FAIL"
                        
                        student_performance.append({
                            'Name': student['name'],
                            'ID': student['id'],
                            'Class': student['class'],
                            'Total Marks': f"{total_marks}/{total_max_marks}",
                            'Percentage': f"{percentage:.1f}%",
                            'Grade': grade,
                            'Status': status
                        })
                
                if student_performance:
                    performance_df = pd.DataFrame(student_performance)
                    
                    # Style the dataframe
                    def style_performance(row):
                        if row['Status'] == 'PASS':
                            return ['background-color: #d4edda'] * len(row)
                        else:
                            return ['background-color: #f8d7da'] * len(row)
                    
                    styled_performance = performance_df.style.apply(style_performance, axis=1)
                    st.dataframe(styled_performance, use_container_width=True, hide_index=True)
                    
                    # Performance distribution chart
                    pass_count = sum(1 for p in student_performance if 'PASS' in p['Status'])
                    fail_count = len(student_performance) - pass_count
                    
                    fig_status = px.pie(
                        values=[pass_count, fail_count],
                        names=['PASS', 'FAIL'],
                        title='Overall Pass/Fail Distribution',
                        color_discrete_map={'PASS': '#28a745', 'FAIL': '#dc3545'}
                    )
                    st.plotly_chart(fig_status, use_container_width=True)
                else:
                    st.info("No performance data available.")
            else:
                st.info("No results data available for analysis.")

# Sidebar information
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
stats = db.get_dashboard_stats()
st.sidebar.write(f"Students: {stats['total_students']}")
st.sidebar.write(f"Subjects: {stats['total_subjects']}")
st.sidebar.write(f"Avg Marks: {stats['avg_marks']}")
st.sidebar.write(f"Pass Rate: {stats['pass_rate']}%")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    "This Student Result Management System helps you manage student data, "
    "subjects, and track academic performance with detailed reports and analytics."
)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Student Result Management System | "
    "Built with Streamlit & SQLite</p>",
    unsafe_allow_html=True
)
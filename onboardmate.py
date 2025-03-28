import os
import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import hashlib
import time
from PIL import Image
import requests
from io import BytesIO
import base64
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import shutil
import json

# Configuration
SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": "your_email@gmail.com",
    "password": "your_app_password"
}
DEFAULT_SESSION_TIMEOUT = 1800  # 30 minutes
AUDIT_LOG = "audit.log"
USER_DB_FILE = "users_db.json"  # File to persist user data

# Security - User authentication
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def generate_secure_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

def password_complexity_check(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char in string.punctuation for char in password):
        return False
    return True

def log_activity(username, action):
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{datetime.now()},{username},{action}\n")

# Load user database from file or create default
def load_user_db():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    else:
        default_users = {
            "ADMIN": {
                "password": make_hashes("Admin@123!"),
                "name": "Admin",
                "access_level": "admin"
            },
            "MANAGER": {
                "password": make_hashes("Manager@123!"),
                "name": "Manager",
                "access_level": "manager"
            },
            "RAJA": {
                "password": make_hashes("9030822289"),
                "name": "Raja",
                "access_level": "admin"
            },
            "ADITHYA": {
                "password": make_hashes("8618781293"),
                "name": "Adithya",
                "access_level": "admin"
            }
        }
        save_user_db(default_users)
        return default_users

# Save user database to file
def save_user_db(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

# Initialize user database
users_db = load_user_db()

def set_video_background():
    video_url = "https://v.ftcdn.net/04/54/98/20/700_F_454982036_NUE8DA4x53AAGkvY45ynWZKn1cenqetu_ST.mp4"
    
    st.markdown(f"""
    <style>
        .stApp {{
            background: transparent;
        }}
        #bg-video {{
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -1;
            opacity: 1;
        }}
        .login-container {{
            max-width: 450px;
            margin: 5% auto;
            padding: 2.5rem;
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            border: 2px solid #B87333;
        }}
        .login-title {{
            text-align: center;
            font-size: 2.2rem;
            margin-bottom: 1.5rem;
            color: #B87333;
            font-weight: 700;
            font-style: italic;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .login-subtitle {{
            text-align: center;
            font-size: 1rem;
            margin-bottom: 2rem;
            color: #ffffff;
            font-weight: 600;
            font-style: italic;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        .stTextInput>div>div>input {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid #B87333;
            color: #000000 !important;
            font-size: 0.95rem;
        }}
        .stTextInput>div>div>input:focus {{
            border-color: #B87333;
            box-shadow: 0 0 0 2px rgba(184, 115, 51, 0.5);
        }}
        .stTextInput>div>div>input::placeholder {{
            color: #666 !important;
        }}
        .stButton>button {{
            width: 100%;
            border-radius: 8px;
            padding: 12px;
            background-color: #B87333;
            color: white;
            font-weight: 600;
            border: none;
            font-size: 1rem;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }}
        .stButton>button:hover {{
            background-color: #A05A2C;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(184, 115, 51, 0.5);
        }}
        .logo-container {{
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        .logo {{
            font-size: 3.5rem;
            color: #B87333;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .error-message {{
            color: #ff6b6b;
            font-weight: 500;
            text-align: center;
            margin-top: 1rem;
            font-size: 0.9rem;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
        }}
        .footer {{
            text-align: center;
            margin-top: 2rem;
            color: #cccccc;
            font-size: 0.8rem;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
        }}
        .input-label {{
            font-weight: 700;
            color: #B87333;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            font-style: italic;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
        }}
    </style>
    
    <video autoplay muted loop id="bg-video">
        <source src="{video_url}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

def premium_login_page():
    """Render the premium MNC-style login page"""
    set_video_background()

    # Login container
    st.markdown("""
    <div class="login-container">
        <div class="logo-container">
            <div class="logo">🔒</div>
            <h1 class="login-title">CORPORATE PORTAL</h1>
            <p class="login-subtitle">Secure access to ONBOARDMATE</p>
        </div>
    """, unsafe_allow_html=True)

    # Login form
    with st.form(key='login_form'):
        st.markdown('<p class="input-label">Username</p>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Enter your corporate ID", label_visibility="collapsed").upper()
        
        st.markdown('<p class="input-label">Password</p>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Enter your password", label_visibility="collapsed")
        
        submit_button = st.form_submit_button(label='SIGN IN', use_container_width=True)

    if submit_button:
        if username in users_db:
            if check_hashes(password, users_db[username]['password']):
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['user_info'] = users_db[username]
                st.session_state['last_activity'] = time.time()
                st.session_state['session_timeout'] = DEFAULT_SESSION_TIMEOUT
                log_activity(username, "LOGIN")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
                log_activity(username, "FAILED_LOGIN")
        else:
            st.error("User not authorized. Contact IT support.")

    # Footer
    st.markdown("""
        <div class="footer">
            <p>© 2024 Enterprise Solutions. All rights reserved.<br>
            v3.0.0 | Secure Login</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

class OnboardMateAgent:
    def __init__(self, api_key, model_name="gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
        )

    def generate_onboarding_plan(self, employee_data):
        prompt_template = """Create a personalized onboarding plan for a new hire with the following details:

        *   **Name:** {name}
        *   **Role:** {role}
        *   **Department:** {department}
        *   **Start Date:** {start_date}
        *   **Previous Experience:** {previous_experience}
        *   **Onboarding Goals:** {goals}

        The plan should include:
        - A checklist of tasks to be completed
        - A schedule of onboarding sessions
        - Links to relevant training materials
        - Key contacts and resources

        Write the onboarding plan in a clear and concise format.
        """
        final_prompt = prompt_template.format(**employee_data)
        chat = self.model.start_chat(history=[])
        try:
            response = chat.send_message(final_prompt)
            if response.candidates and response.candidates[0].finish_reason == "RECITATION":
                print("RECITATION STOPPED")
                return None
            else:
                return response.text
        except genai.types.generation_types.StopCandidateException as e:
            print(f"Error: {e}")
            return None

    def provide_knowledge_assistance(self, query):
        response = self.model.start_chat(history=[]).send_message(
            f"Provide a detailed response to the following query from a new hire:\n\n{query}"
        )
        return response.text

def send_notification(email, subject, content):
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['username']
    msg['To'] = email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(content, 'html'))
    
    try:
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.starttls()
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def generate_pdf(content, employee_data, file_name="onboarding_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    # Add header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ONBOARDING PLAN", ln=True, align='C')
    pdf.ln(10)
    
    # Add employee info
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Employee Information", ln=True)
    pdf.set_font("Arial", '', 10)
    
    info = f"""
    Name: {employee_data['name']}
    Role: {employee_data['role']}
    Department: {employee_data['department']}
    Start Date: {employee_data['start_date']}
    """
    
    for line in info.split('\n'):
        pdf.cell(200, 6, txt=line.strip(), ln=True)
    
    # Add onboarding content
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Onboarding Plan", ln=True)
    pdf.set_font("Arial", '', 10)
    
    for line in content.split('\n'):
        pdf.cell(200, 6, txt=line.strip(), ln=True)
    
    # Add footer
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 6, txt=f"Generated on {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    
    pdf.output(file_name)
    return file_name

def save_to_excel(data, file_path="onboarding_data.xlsx"):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        new_df = pd.DataFrame([data])
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_excel(file_path, index=False)

def display_dashboard_metrics():
    if os.path.exists("onboarding_data.xlsx"):
        df = pd.read_excel("onboarding_data.xlsx")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Employees", len(df))
        with col2:
            st.metric("Departments", df['department'].nunique())
        with col3:
            latest = pd.to_datetime(df['start_date']).max()
            st.metric("Latest Hire", latest.strftime('%Y-%m-%d'))
        
        st.subheader("Onboarding Analytics")
        tab1, tab2 = st.tabs(["Department Distribution", "Timeline"])
        
        with tab1:
            dept_counts = df['department'].value_counts()
            st.bar_chart(dept_counts)
        
        with tab2:
            timeline = df.groupby(pd.to_datetime(df['start_date']).dt.to_period('M')).size().cumsum()
            st.line_chart(timeline)

def main_app():
    st.set_page_config(
        page_title="OnboardMate PRO - AI-Powered Employee Onboarding",
        page_icon="👑",
        layout="wide",
    )

    # Initialize session timeout if not set
    if 'session_timeout' not in st.session_state:
        st.session_state.session_timeout = DEFAULT_SESSION_TIMEOUT

    # Session timeout check
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = time.time()
    else:
        if time.time() - st.session_state.last_activity > st.session_state.session_timeout:
            st.warning("Session timed out due to inactivity")
            st.session_state.clear()
            st.rerun()
        st.session_state.last_activity = time.time()

    # Premium sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="background-color:#4a6bff;padding:15px;border-radius:10px;color:white;">
            <h3 style="color:white;">👑 OnboardMate PRO</h3>
            <p>Welcome, <strong>{st.session_state['user_info']['name']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            log_activity(st.session_state['username'], "LOGOUT")
            st.session_state.clear()
            st.rerun()

    # Main content
    st.title("👑 OnboardMate PRO - AI-Powered Employee Onboarding")
    st.markdown("Premium employee onboarding experience powered by AI")

    # Dashboard metrics
    display_dashboard_metrics()

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("API key not found in environment variables! Set GEMINI_API_KEY.")
        return

    onboard_mate_agent = OnboardMateAgent(api_key)
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Onboarding Plan", "📚 Knowledge Assistance", "📁 Documents", "⚙️ Admin"])

    with tab1:
        st.subheader("📋 Onboarding Plan")
        st.markdown("Please provide the following details for the new hire:")

        name = st.text_input("Name", placeholder="e.g. AKELLA SRI DATTA SURYANARAYANA", key="onboard_name")
        role = st.text_input("Role", placeholder="e.g. Software Engineer", key="onboard_role")
        department = st.text_input("Department", placeholder="e.g. Engineering", key="onboard_department")
        start_date = st.date_input("Start Date", key="onboard_start_date")
        previous_experience = st.text_area("Previous Experience", placeholder="e.g. 5 years of experience in software development", key="onboard_experience")
        goals = st.text_area("Onboarding Goals", placeholder="e.g. Get familiar with the codebase, understand the team's workflow", key="onboard_goals")

        if st.button("Generate Onboarding Plan", key="btn_generate_plan"):
            if all([name.strip(), role.strip(), department.strip(), start_date, previous_experience.strip(), goals.strip()]):
                employee_data = {
                    "name": name,
                    "role": role,
                    "department": department,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "previous_experience": previous_experience,
                    "goals": goals,
                }
                with st.spinner("Generating premium onboarding plan..."):
                    onboarding_plan = onboard_mate_agent.generate_onboarding_plan(employee_data)
                if onboarding_plan:
                    st.markdown("### Generated Onboarding Plan")
                    st.markdown(onboarding_plan, unsafe_allow_html=True)
                    save_to_excel(employee_data)
                    st.success("Employee details saved to Excel file.")
                    pdf_file = generate_pdf(onboarding_plan, employee_data)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                label="📥 Download PDF",
                                data=f,
                                file_name="onboarding_plan.pdf",
                                mime="application/pdf",
                            )
                    
                    with col2:
                        if st.checkbox("Send email notification to HR"):
                            hr_email = st.text_input("HR Email Address", key="hr_email")
                            if st.button("Send Notification"):
                                if send_notification(
                                    hr_email,
                                    f"New Onboarding Plan for {name}",
                                    f"<h1>New Onboarding Plan</h1><p>{onboarding_plan}</p>"
                                ):
                                    st.success("Notification sent successfully!")
                                    log_activity(st.session_state['username'], f"SENT_NOTIFICATION {hr_email}")
                    
                    log_activity(st.session_state['username'], f"GENERATED_PLAN {name}")
                else:
                    st.error("Onboarding plan generation failed. Please adjust the inputs.")
            else:
                st.warning("Please provide all required details for the onboarding plan.")

        if os.path.exists("onboarding_data.xlsx"):
            st.subheader("📊 Saved Employee Data")
            df = pd.read_excel("onboarding_data.xlsx")
            st.dataframe(df)

    with tab2:
        st.subheader("📚 Knowledge Assistance")
        st.markdown("Ask any question related to your onboarding process or role.")

        # Example questions section
        st.markdown("### Example Questions")
        example_questions = [
            "Where can I find the project documentation?",
            "What is the process for requesting time off?",
            "How do I set up my email account?",
            "Where can I find the employee handbook?",
            "What are the core working hours?",
            "How do I access the company's intranet?",
        ]
        
        # Display example questions as clickable chips
        cols = st.columns(3)
        for i, question in enumerate(example_questions):
            with cols[i % 3]:
                if st.button(question, key=f"example_q_{i}"):
                    st.session_state.knowledge_query = question

        # Input field for knowledge query
        query = st.text_area(
            "Enter your query", 
            value=st.session_state.get("knowledge_query", ""),
            placeholder="e.g. Where can I find the project documentation?", 
            key="knowledge_query"
        )

        if st.button("Get Assistance", key="btn_get_assistance"):
            if query.strip():
                with st.spinner("Fetching knowledge assistance..."):
                    knowledge_response = onboard_mate_agent.provide_knowledge_assistance(query)
                st.markdown("### Knowledge Assistance")
                st.markdown(knowledge_response, unsafe_allow_html=True)
                log_activity(st.session_state['username'], f"KNOWLEDGE_QUERY {query[:50]}...")
            else:
                st.warning("Please enter a query to get assistance.")

        # General FAQs section
        st.markdown("### General FAQs")
        faqs = {
            "How do I set up my email account?": "You can set up your email account by following the instructions provided in the onboarding email. If you need further assistance, contact IT support.",
            "What is the process for requesting time off?": "You can request time off by submitting a request through the HR portal. Make sure to get approval from your manager.",
            "Where can I find the employee handbook?": "The employee handbook is available on the company's intranet under the 'Resources' section.",
            "What are the core working hours?": "The core working hours are from 9 AM to 5 PM, Monday to Friday.",
            "How do I access the company's intranet?": "You can access the intranet by logging in with your company credentials at intranet.company.com.",
            "What is the dress code policy?": "The company follows a business casual dress code. Please refer to the employee handbook for more details.",
            "How do I request IT support?": "You can request IT support by submitting a ticket through the IT support portal or by calling the IT helpdesk.",
            "What are the key contacts in my department?": "You can find the key contacts in your department by checking the department directory on the intranet.",
            "How do I enroll in benefits?": "You can enroll in benefits by logging into the HR portal and following the enrollment instructions.",
            "What is the process for submitting expenses?": "You can submit expenses by filling out the expense report form available on the HR portal and submitting it for approval.",
            "How do I access training materials?": "Training materials are available on the company's learning management system (LMS). You can access it through the intranet.",
            "What is the company's policy on remote work?": "The company allows remote work for certain roles. Please check with your manager and refer to the remote work policy in the employee handbook.",
            "How do I schedule a meeting room?": "You can schedule a meeting room by using the room booking system available on the intranet.",
            "What are the company's core values?": "The company's core values are integrity, innovation, collaboration, and excellence.",
            "How do I report a technical issue?": "You can report a technical issue by submitting a ticket through the IT support portal or by contacting the IT helpdesk.",
            "What is the process for performance reviews?": "Performance reviews are conducted bi-annually. You will receive a notification from HR with instructions on how to prepare.",
            "How do I update my personal information in the system?": "You can update your personal information by logging into the HR portal and navigating to the 'My Profile' section.",
            "What are the company's social media guidelines?": "The company's social media guidelines are available in the employee handbook. Please review them before posting on social media.",
            "How do I request business cards?": "You can request business cards by submitting a request through the HR portal. Make sure to include your design preferences.",
        }
        
        # Filter out FAQs that are already in example questions
        filtered_faqs = {k: v for k, v in faqs.items() if k not in example_questions}
        
        # Display filtered FAQs
        for question, answer in filtered_faqs.items():
            with st.expander(question):
                st.markdown(answer)

    with tab3:
        st.subheader("📁 Document Management")
        st.markdown("Upload and manage company documents")
        
        uploaded_files = st.file_uploader("Upload documents", 
                                        accept_multiple_files=True,
                                        type=['pdf', 'docx', 'pptx', 'xlsx', 'txt', 'png', 'jpg'])
        
        if uploaded_files:
            os.makedirs("company_docs", exist_ok=True)
            for file in uploaded_files:
                with open(f"company_docs/{file.name}", "wb") as f:
                    f.write(file.getbuffer())
            st.success(f"{len(uploaded_files)} files uploaded successfully!")
            log_activity(st.session_state['username'], f"UPLOADED_DOCS {len(uploaded_files)} files")
        
        if os.path.exists("company_docs"):
            docs = os.listdir("company_docs")
            if docs:
                selected = st.selectbox("View document", docs)
                if selected:
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.write(f"Selected: {selected}")
                    with col2:
                        with open(f"company_docs/{selected}", "rb") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=selected
                            )
                    if st.button("Delete", key=f"del_{selected}"):
                        os.remove(f"company_docs/{selected}")
                        st.success(f"Deleted {selected}")
                        log_activity(st.session_state['username'], f"DELETED_DOC {selected}")
                        st.rerun()

    with tab4:
        if st.session_state['user_info']['access_level'] == "admin":
            st.subheader("⚙️ Admin Panel")
            
            admin_tab1, admin_tab2, admin_tab3 = st.tabs(["User Management", "Audit Logs", "System Settings"])
            
            with admin_tab1:
                st.markdown("### User Accounts")
                
                # Display current users in an editable dataframe
                user_df = pd.DataFrame.from_dict(users_db, orient='index')
                user_df['username'] = user_df.index
                user_df = user_df[['username', 'name', 'access_level']]
                
                # Display the dataframe with delete buttons for each row
                for _, row in user_df.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
                    with col1:
                        st.text_input("Username", value=row['username'], key=f"username_{row['username']}", disabled=True)
                    with col2:
                        st.text_input("Full Name", value=row['name'], key=f"name_{row['username']}")
                    with col3:
                        access = st.selectbox(
                            "Access Level",
                            ["admin", "manager"],
                            index=0 if row['access_level'] == "admin" else 1,
                            key=f"access_{row['username']}"
                        )
                    with col4:
                        if st.button("🗑️ Delete", key=f"delete_{row['username']}"):
                            if row['username'] == st.session_state['username']:
                                st.error("You cannot delete your own account!")
                            else:
                                del users_db[row['username']]
                                save_user_db(users_db)
                                st.success(f"User {row['username']} deleted successfully!")
                                log_activity(st.session_state['username'], f"DELETED_USER {row['username']}")
                                st.rerun()
                
                # Save changes button
                if st.button("💾 Save Changes", key="save_user_changes"):
                    for _, row in user_df.iterrows():
                        username = row['username']
                        users_db[username]['name'] = st.session_state[f"name_{username}"]
                        users_db[username]['access_level'] = st.session_state[f"access_{username}"]
                    save_user_db(users_db)
                    st.success("User changes saved successfully!")
                    log_activity(st.session_state['username'], "UPDATED_USERS")
                    st.rerun()
                
                # Add new user section
                st.markdown("### Add New User")
                with st.form(key='add_user_form'):
                    new_username = st.text_input("Username", key="new_user").upper()
                    new_name = st.text_input("Full Name", key="new_name")
                    new_password = st.text_input("Password", type="password", key="new_pass")
                    new_access = st.selectbox("Access Level", ["admin", "manager"], key="new_access")
                    
                    if st.form_submit_button("Create User"):
                        if new_username and new_name and new_password:
                            if new_username in users_db:
                                st.error("Username already exists")
                            else:
                                if password_complexity_check(new_password):
                                    users_db[new_username] = {
                                        "password": make_hashes(new_password),
                                        "name": new_name,
                                        "access_level": new_access
                                    }
                                    save_user_db(users_db)
                                    st.success("User created successfully!")
                                    log_activity(st.session_state['username'], f"CREATED_USER {new_username}")
                                    st.rerun()
                                else:
                                    st.error("Password must be at least 8 characters with uppercase, number, and special character")
                        else:
                            st.error("All fields are required")
            
            with admin_tab2:
                st.markdown("### Audit Logs")
                if os.path.exists(AUDIT_LOG):
                    logs = pd.read_csv(AUDIT_LOG, names=["timestamp", "user", "action"])
                    st.dataframe(logs.sort_values("timestamp", ascending=False))
                    
                    if st.button("Clear Logs"):
                        open(AUDIT_LOG, 'w').close()
                        st.success("Audit logs cleared")
                        log_activity(st.session_state['username'], "CLEARED_LOGS")
                        st.rerun()
                else:
                    st.info("No audit logs available")
            
            with admin_tab3:
                st.markdown("### System Configuration")
                
                new_timeout = st.number_input("Session Timeout (minutes)", 
                              value=st.session_state.session_timeout//60, 
                              min_value=1, 
                              max_value=120,
                              key="session_timeout")
                
                if st.button("Save Settings"):
                    st.session_state.session_timeout = new_timeout * 60
                    st.success("Settings saved")
                    log_activity(st.session_state['username'], "UPDATED_SETTINGS")
        else:
            st.warning("You don't have permission to access this section")

def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        premium_login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
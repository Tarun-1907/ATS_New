from dotenv import load_dotenv
import streamlit as st
import os
from PyPDF2 import PdfReader
from groq import Groq
from streamlit_option_menu import option_menu
import io

# Load environment variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Set page config with professional theme
st.set_page_config(
    page_title="Resume Analyzer Pro | ATS Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #4a6fa5;
            color: white;
            border-radius: 5px;
            padding: 10px 24px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #3a5a80;
            transform: scale(1.02);
        }
        .stTextArea>div>div>textarea {
            border: 1px solid #ced4da;
            border-radius: 5px;
        }
        .stFileUploader>div>div>div>button {
            background-color: #4a6fa5;
            color: white;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #2c3e50;
        }
        .premium-feature {
            border-left: 4px solid #ffd700;
            padding-left: 1rem;
            background-color: rgba(255, 215, 0, 0.1);
            margin-bottom: 1rem;
        }
        .feature-card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Session state for premium features
if 'premium_user' not in st.session_state:
    st.session_state.premium_user = False

def llama_response(text_prompt):
    """Send prompt to Llama model via Groq API"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": text_prompt}],
            model="llama3-70b-8192",
            temperature=0.3,
            max_tokens=8192,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {str(e)}")
        return None

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF using PyPDF2"""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text if text else "Could not extract text (may be image-based PDF)"
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

def show_pdf_preview(uploaded_file):
    """Show PDF preview using PyPDF2 (text preview only)"""
    try:
        text = extract_text_from_pdf(uploaded_file)
        if text:
            st.text_area("PDF Text Preview", value=text[:2000] + "..." if len(text) > 2000 else text, height=300)
        else:
            st.warning("Could not extract text for preview")
    except Exception as e:
        st.error(f"Couldn't display preview: {str(e)}")

# Premium analysis functions
def premium_analysis(job_desc, resume_text):
    """Premium analysis with more detailed insights"""
    premium_prompts = {
        "career_path": """
        Analyze the candidate's resume and the provided job description to suggest potential career paths 
        and growth opportunities. Consider the candidate's current skills, experience, and how they align 
        with industry trends. Provide a 5-year career projection with recommended skills to acquire.
        """,
        "salary_benchmark": """
        Based on the candidate's qualifications and the job requirements, provide a salary benchmark 
        for this position in different regions (US, Europe, Asia). Include factors that might affect 
        compensation and negotiation tips.
        """,
        "competitor_analysis": """
        Compare this resume against typical candidates for this position. Highlight competitive 
        advantages and potential gaps compared to top performers in this role. Provide actionable 
        insights to become a top-tier candidate.
        """
    }
    
    results = {}
    with st.spinner("Running premium analysis..."):
        for name, prompt in premium_prompts.items():
            full_prompt = f"Job Description:\n{job_desc}\n\nResume Content:\n{resume_text}\n\nTask:\n{prompt}"
            results[name] = llama_response(full_prompt)
    
    return results

# Sidebar with navigation and premium upgrade
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    
    if not st.session_state.premium_user:
        st.markdown("### Upgrade to Premium")
        st.markdown("""
        - Career path projections
        - Salary benchmarking
        - Competitor analysis
        - AI-powered resume rewriting
        - Unlimited analysis
        """)
        if st.button("✨ Upgrade Now", key="upgrade_btn"):
            st.session_state.premium_user = True
            st.success("Premium features unlocked!")
            st.rerun()
    else:
        st.success("Premium Member")
        if st.button("⬅️ Back to Basic", key="downgrade_btn"):
            st.session_state.premium_user = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown("""
    1. Enter job description
    2. Upload your resume (PDF)
    3. Select analysis type
    4. Get instant feedback
    """)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    Resume Analyzer Pro uses advanced AI to help you optimize your resume for Applicant Tracking Systems 
    and stand out to recruiters.
    """)

# Main app content
st.title("📄 Resume Analyzer Pro")
st.markdown("Optimize your resume for Applicant Tracking Systems and get detailed feedback")

# Navigation
selected = option_menu(
    menu_title=None,
    options=["Basic Analysis", "Premium Features", "Resume Tips"],
    icons=["clipboard-check", "stars", "lightbulb"],
    orientation="horizontal"
)

if selected == "Basic Analysis":
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Job Description Analysis")
        job_description = st.text_area("Paste the job description here:", height=200, key="input")
        
        if not job_description:
            st.warning("Please enter a job description to analyze against")
        
        st.subheader("Resume Upload")
        uploaded_file = st.file_uploader("Upload your resume (PDF only):", type=["pdf"], label_visibility="collapsed")
        
        resume_text = ""
        if uploaded_file:
            st.success("Resume uploaded successfully!")
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if st.checkbox("Show quick preview", key="preview_check"):
                show_pdf_preview(uploaded_file)
    
    with col2:
        st.subheader("Analysis Options")
        
        if st.button("🔍 Basic Resume Evaluation", help="Get a general evaluation of your resume against the job description"):
            if uploaded_file and job_description and resume_text:
                with st.spinner("Analyzing your resume..."):
                    try:
                        prompt = f"""
                        You are an experienced Technical expert and HR in the field of computer science. 
                        Your task is to review the provided resume against this job description:
                        
                        Job Description:
                        {job_description}
                        
                        Resume Content:
                        {resume_text}
                        
                        Please share your professional evaluation on whether the candidate's profile aligns with the role. 
                        Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
                        """
                        response = llama_response(prompt)
                        
                        with st.expander("📋 Evaluation Results", expanded=True):
                            st.write(response)
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
            else:
                st.warning("Please upload a resume and enter a job description")
        
        if st.button("📊 ATS Match Percentage", help="See how well your resume matches the job description"):
            if uploaded_file and job_description and resume_text:
                with st.spinner("Calculating match score..."):
                    try:
                        prompt = f"""
                        You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of Computer Science Engineering and Technology field and ATS functionality. 
                        Your task is to evaluate this resume against the provided job description:
                        
                        Job Description:
                        {job_description}
                        
                        Resume Content:
                        {resume_text}
                        
                        Give me the percentage of match if the resume matches the job description. 
                        First, the output should come as a percentage. 
                        Then list keywords missing in the resume. 
                        Finally provide your overall assessment.
                        """
                        response = llama_response(prompt)
                        
                        with st.expander("📈 Match Results", expanded=True):
                            st.write(response)
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
            else:
                st.warning("Please upload a resume and enter a job description")
        
        if st.button("🛠 Improvement Suggestions", help="Get actionable advice to improve your resume"):
            if uploaded_file and job_description and resume_text:
                with st.spinner("Generating improvement suggestions..."):
                    try:
                        prompt = f"""
                        You are a expert in computer science field with 30 years of experience. 
                        After evaluating this resume against the job description:
                        
                        Job Description:
                        {job_description}
                        
                        Resume Content:
                        {resume_text}
                        
                        Tell the candidate how they can improve their resume by:
                        1. Addressing missing skills
                        2. Suggesting how to acquire those skills
                        3. Highlighting key points to emphasize
                        4. Recommending structural improvements
                        """
                        response = llama_response(prompt)
                        
                        with st.expander("🔧 Improvement Suggestions", expanded=True):
                            st.write(response)
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
            else:
                st.warning("Please upload a resume and enter a job description")

elif selected == "Premium Features":
    if not st.session_state.premium_user:
        st.warning("Premium features require an upgrade")
        st.markdown("""
        <div class="feature-card">
            <h3>✨ Premium Features</h3>
            <ul>
                <li><strong>Career Path Projection:</strong> See where your skills can take you</li>
                <li><strong>Salary Benchmarking:</strong> Know your worth in different markets</li>
                <li><strong>Competitor Analysis:</strong> See how you compare to other candidates</li>
                <li><strong>AI Resume Rewriting:</strong> Let our AI optimize your resume wording</li>
                <li><strong>Unlimited Analysis:</strong> No restrictions on number of reviews</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👉 Upgrade to Premium Now", key="premium_upgrade"):
            st.session_state.premium_user = True
            st.rerun()
    else:
        st.success("You have access to premium features!")
        
        if 'job_description' not in st.session_state:
            st.session_state.job_description = ""
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None
        if 'resume_text' not in st.session_state:
            st.session_state.resume_text = ""
            
        st.session_state.job_description = st.text_area("Job Description:", value=st.session_state.job_description, height=150)
        st.session_state.uploaded_file = st.file_uploader("Upload Resume (PDF):", type=["pdf"])
        
        if st.session_state.uploaded_file:
            st.session_state.resume_text = extract_text_from_pdf(st.session_state.uploaded_file)
        
        if st.button("🚀 Run Premium Analysis"):
            if st.session_state.uploaded_file and st.session_state.job_description and st.session_state.resume_text:
                with st.spinner("Running comprehensive premium analysis..."):
                    try:
                        results = premium_analysis(st.session_state.job_description, st.session_state.resume_text)
                        
                        st.subheader("Premium Analysis Results")
                        
                        with st.expander("📈 Career Path Projection", expanded=True):
                            st.markdown(results['career_path'])
                        
                        with st.expander("💰 Salary Benchmarking"):
                            st.markdown(results['salary_benchmark'])
                        
                        with st.expander("🆚 Competitor Analysis"):
                            st.markdown(results['competitor_analysis'])
                        
                        # Additional premium feature - AI resume rewriting
                        with st.expander("✍️ AI-Powered Resume Rewrite (Beta)"):
                            rewrite_prompt = f"""
                            Rewrite this resume to better match the job description while maintaining all factual information. 
                            Focus on optimizing for ATS systems and improving impact. Keep the same format but enhance the wording.
                            
                            Job Description:
                            {st.session_state.job_description}
                            
                            Original Resume:
                            {st.session_state.resume_text}
                            
                            Provide the rewritten version with clear section headings.
                            """
                            rewritten = llama_response(rewrite_prompt)
                            st.markdown(rewritten)
                            st.download_button(
                                label="Download Rewritten Resume",
                                data=rewritten,
                                file_name="optimized_resume.txt",
                                mime="text/plain"
                            )
                    
                    except Exception as e:
                        st.error(f"Premium analysis failed: {str(e)}")
            else:
                st.warning("Please upload a resume and enter a job description")

elif selected == "Resume Tips":
    st.subheader("Professional Resume Tips")
    
    tab1, tab2, tab3 = st.tabs(["ATS Optimization", "Content Tips", "Formatting Guidelines"])
    
    with tab1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔍 ATS Optimization Tips</h4>
            <ul>
                <li>Use standard section headings (e.g., "Work Experience", "Education")</li>
                <li>Include keywords from the job description naturally</li>
                <li>Avoid tables, columns, and graphics that might confuse ATS</li>
                <li>Use common fonts like Arial, Times New Roman, or Calibri</li>
                <li>Save as PDF unless specified otherwise</li>
                <li>Don't use headers/footers for critical information</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="feature-card">
            <h4>📝 Content Tips</h4>
            <ul>
                <li>Focus on achievements rather than responsibilities</li>
                <li>Use action verbs and quantify results when possible</li>
                <li>Tailor your resume for each job application</li>
                <li>Keep it concise (1-2 pages for most professionals)</li>
                <li>Include relevant skills and certifications</li>
                <li>Proofread multiple times for errors</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        <div class="feature-card">
            <h4>🎨 Formatting Guidelines</h4>
            <ul>
                <li>Maintain consistent formatting throughout</li>
                <li>Use 10-12pt font size for body text</li>
                <li>Leave adequate white space (1-inch margins)</li>
                <li>Use bold/italic sparingly for emphasis</li>
                <li>List experience in reverse chronological order</li>
                <li>Ensure good contrast between text and background</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Common Mistakes to Avoid")
    st.markdown("""
    - Spelling and grammatical errors
    - Including irrelevant personal information
    - Using unprofessional email addresses
    - Listing every job you've ever had
    - Being too vague or using clichés
    - Including references on the resume
    - Using an outdated format
    """)
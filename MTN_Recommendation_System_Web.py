# -*- coding: utf-8 -*-
"""
MTN Recommendation System - Web Version
A Streamlit web application for AI-powered product recommendations
"""

import os
import re
import time
import pandas as pd
import streamlit as st
from io import StringIO, BytesIO  # Added BytesIO import here
import matplotlib.pyplot as plt
from PIL import Image
from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

# Constants
LOGO_FILE = "New-mtn-logo.jpg"
SUBSCRIBER_FILE = "SubscriberProfileData.csv"
PRODUCT_FILE = "ProductCatalogue.csv"
CREDENTIALS_FILE = "hackathon2025-454908-0a52f19ef9b1.json"

# Category colors for visualization
category_colors = {
    "Data": "#4285F4",  # Blue
    "Voice": "#EA4335",  # Red
    "SMS": "#FBBC05",   # Yellow
    "Bundle": "#34A853", # Green
    "VAS": "#8E24AA",    # Purple
    "Other": "#9E9E9E"   # Grey
}

# Set page configuration
st.set_page_config(
    page_title="MTN Recommendation System",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Google Cloud credentials
def initialize_google_cloud():
    try:
        if os.path.exists(CREDENTIALS_FILE):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
            aiplatform.init()
            return True
        else:
            st.error(f"Google Cloud credentials file not found: {CREDENTIALS_FILE}")
            return False
    except Exception as e:
        st.error(f"Failed to initialize Google Cloud: {str(e)}")
        return False

# Check integration health
def check_integration_health():
    status = {
        "Google Cloud API": False,
        "Data Files": False,
        "Gemini AI": False
    }
    
    tooltips = {
        "Google Cloud API": "Connection to Google Cloud services",
        "Data Files": "Required data files for analysis",
        "Gemini AI": "Access to Gemini AI model"
    }
    
    # Check Google Cloud API
    try:
        if os.path.exists(CREDENTIALS_FILE):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
            aiplatform.init()
            status["Google Cloud API"] = True
    except:
        pass
    
    # Check data files
    if os.path.exists(SUBSCRIBER_FILE) and os.path.exists(PRODUCT_FILE):
        status["Data Files"] = True
    
    # Check Gemini AI
    try:
        model = GenerativeModel("gemini-1.5-flash-001")
        response = model.generate_content("Hello")
        if response:
            status["Gemini AI"] = True
    except:
        pass
    
    return status, tooltips

# Load MTN logo
@st.cache_data
def load_logo():
    try:
        if os.path.exists(LOGO_FILE):
            return Image.open(LOGO_FILE)
        return None
    except Exception as e:
        st.error(f"Failed to load logo: {str(e)}")
        return None

# Load data files
@st.cache_data
def load_data():
    try:
        subscriber_df = pd.read_csv(SUBSCRIBER_FILE, on_bad_lines='skip')
        product_df = pd.read_csv(PRODUCT_FILE, on_bad_lines='skip')
        
        # Clean column names
        subscriber_df.columns = [str(col).strip() for col in subscriber_df.columns]
        product_df.columns = [str(col).strip() for col in product_df.columns]
        
        return subscriber_df, product_df
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return None, None

# Extract bullet points from text
def extract_bullet_points(text):
    # Find bullet points in the text
    bullet_pattern = r"[-•*]\s*(.*?)(?=\n[-•*]|\n\n|$)"
    bullets = re.findall(bullet_pattern, text, re.DOTALL)
    return [b.strip() for b in bullets if b.strip()]

# Format markdown text
def format_markdown_text(text):
    # Replace Markdown bullet points with proper bullet symbols
    formatted_text = re.sub(r'^\s*\*\s+', '• ', text, flags=re.MULTILINE)
    # Replace nested Markdown bullet points
    formatted_text = re.sub(r'^\s+\*\s+', '    • ', formatted_text, flags=re.MULTILINE)
    return formatted_text

# Generate recommendations
def generate_recommendations(selected_subscribers, product_df, variables):
    with st.spinner("Generating AI recommendations..."):
        try:
            model = GenerativeModel("gemini-1.5-flash-001")
            
            subscriber_data_str = selected_subscribers.to_string(index=False)
            product_data_str = product_df.to_string(index=False)
            filters = "\n".join(f"- Include {k}" for k, v in variables.items() if v)
            
            prompt = f"""
Compare the data and use it to compare with the product catalogue below. Recommend one product for each of the following subscribers:

{subscriber_data_str}

Use the product catalogue below:

{product_data_str}

Variables to consider for profiling:
{filters}

Output a clean markdown-style table with the following columns exactly:
MSISDN | RecommendedProduct  | Category | Tier | ProductPrice | Reason | UpsellOption | CrossSellOption
use product names instead of product codes
After the table, include a short bullet-point section with additional upsell and cross-sell insights or strategy tips. Do not include general commentary—just the table and the follow-up list.
always make the recommendations always.
"""
            
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Extract table from response
            potential_table_match = re.search(r"((?:\|.+\|\n)+)", response_text)
            table_df = None
            if potential_table_match:
                table_text = potential_table_match.group(1)
                try:
                    table_df = pd.read_csv(StringIO(table_text), sep="|", engine='python')
                    table_df = table_df.dropna(axis=1, how='all').dropna(axis=0, how='all')
                    table_df.columns = [col.strip() for col in table_df.columns]
                except:
                    table_df = None
            
            # Extract explanation text
            explanation_text = response_text.replace(table_text, "") if potential_table_match else "No additional upsell/cross-sell insights were provided."
            
            return table_df, explanation_text, response_text
        except Exception as e:
            st.error(f"Failed to generate recommendations: {str(e)}")
            return None, f"Error: {str(e)}", None

# Create comparison chart
def create_comparison_chart(table_df):
    if table_df is not None:
        # Count recommendations by category
        category_counts = table_df['Category'].value_counts()
        
        # Create a bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(
            category_counts.index, 
            category_counts.values,
            color=[category_colors.get(str(cat).strip(), category_colors["Other"]) for cat in category_counts.index]
        )
        
        # Add labels and title
        ax.set_xlabel('Category')
        ax.set_ylabel('Count')
        ax.set_title('Product Recommendation Distribution by Category')
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    return None

# Main application
def main():
    # Initialize Google Cloud
    cloud_initialized = initialize_google_cloud()
    
    # Initialize session state variables
    if "has_run_analysis" not in st.session_state:
        st.session_state.has_run_analysis = False
    if "table_df" not in st.session_state:
        st.session_state.table_df = None
    if "explanation_text" not in st.session_state:
        st.session_state.explanation_text = None
    if "full_response" not in st.session_state:
        st.session_state.full_response = None
    if "selected_subscribers" not in st.session_state:
        st.session_state.selected_subscribers = None
    if "selection_mode" not in st.session_state:
        st.session_state.selection_mode = None
    if "variables" not in st.session_state:
        st.session_state.variables = None
    
    # Display MTN logo
    logo = load_logo()
    if logo:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo, width=200)
    
    # App title
    st.title("MTN AI Product Recommendation System")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Health check section
        st.subheader("System Health")
        status, tooltips = check_integration_health()
        for service, ok in status.items():
            if ok:
                st.success(f"{service}: OK - {tooltips[service]}")
            else:
                st.error(f"{service}: FAILED - {tooltips[service]}")
        
        if st.button("Refresh Health Check"):
            st.rerun()
        
        st.markdown("---")
        
        # MSISDN selection
        st.subheader("MSISDN Selection")
        selection_mode = st.radio(
            "Select MSISDN Input Method:",
            ["Specific MSISDN", "Random sample of MSISDNs", "All MSISDNs"],
            index=1
        )
        
        if selection_mode == "Specific MSISDN":
            specific_msisdn = st.text_input("Enter MSISDN:")
        elif selection_mode == "Random sample of MSISDNs":
            random_count = st.number_input("Number of random MSISDNs:", min_value=1, max_value=20, value=4)
        
        # Variables to consider
        st.subheader("Profiling Variables")
        variables = {}
        for field in ["DemographicSegment", "DeviceType", "CurrentPlan", "VASUsed"]:
            variables[field] = st.checkbox(field, value=True)
        
        # Run button
        run_button = st.button("Run Analysis", type="primary")
    
    # Main content
    if not cloud_initialized:
        st.warning("Google Cloud API is not initialized. Please check your credentials.")
    
    # Load data
    subscriber_df, product_df = load_data()
    if subscriber_df is None or product_df is None:
        st.error("Failed to load data files. Please check if the files exist.")
        return
    
    # Run analysis when button is clicked
    if run_button:
        # Select subscribers based on mode
        if selection_mode == "Specific MSISDN":
            try:
                msisdn = int(specific_msisdn)
                selected_subscribers = subscriber_df[subscriber_df['MSISDN'] == msisdn]
                if selected_subscribers.empty:
                    st.error(f"MSISDN {msisdn} not found in dataset.")
                    return
            except:
                st.error("Invalid MSISDN format. Please enter a valid number.")
                return
        elif selection_mode == "Random sample of MSISDNs":
            selected_subscribers = subscriber_df.sample(min(random_count, len(subscriber_df)))
        else:  # All MSISDNs
            selected_subscribers = subscriber_df.copy()
        
        # Generate recommendations
        table_df, explanation_text, full_response = generate_recommendations(
            selected_subscribers, product_df, variables
        )
        
        # Store results in session state
        st.session_state.has_run_analysis = True
        st.session_state.table_df = table_df
        st.session_state.explanation_text = explanation_text
        st.session_state.full_response = full_response
        st.session_state.selected_subscribers = selected_subscribers
        st.session_state.selection_mode = selection_mode
        st.session_state.variables = variables
    
    # Display results if analysis has been run
    if st.session_state.has_run_analysis and st.session_state.table_df is not None:
        # Use session state variables
        table_df = st.session_state.table_df
        explanation_text = st.session_state.explanation_text
        full_response = st.session_state.full_response
        selected_subscribers = st.session_state.selected_subscribers
        selection_mode = st.session_state.selection_mode
        variables = st.session_state.variables
        
        # Display results in tabs
        tabs = st.tabs(["Recommendations", "Upsell & Cross-sell Insights", "Comparison View", "Raw Data"])
        
        # Recommendations tab
        with tabs[0]:
            st.subheader("Selected Subscribers")
            st.dataframe(selected_subscribers, use_container_width=True)
            
            st.subheader("Recommended Products")
            # Modified styling to be more subtle and improve visibility
            st.dataframe(
                table_df.style.apply(
                    lambda x: ['background-color: ' + category_colors.get(str(x['Category']).strip(), category_colors["Other"]) 
                                  + '; opacity: 0.3' for _ in x],  # Reduced opacity for better visibility
                    axis=1
                ),
                use_container_width=True
            )
            
            # Download buttons - modified to prevent page reload
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = table_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download CSV",
                    csv,
                    f"MTN_Recommendations_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                    key='download-csv',
                    on_click=lambda: None  # Prevents reload
                )
            
            with col2:
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    table_df.to_excel(writer, sheet_name='Recommendations', index=False)
                excel_data = buffer.getvalue()
                st.download_button(
                    "Download Excel",
                    excel_data,
                    f"MTN_Recommendations_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    "application/vnd.ms-excel",
                    key='download-excel',
                    on_click=lambda: None  # Prevents reload
                )
            
            with col3:
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    selected_subscribers.to_excel(writer, sheet_name='Subscribers', index=False)
                    table_df.to_excel(writer, sheet_name='Recommendations', index=False)
                    insights_df = pd.DataFrame({'Insights': [explanation_text.strip()]})
                    insights_df.to_excel(writer, sheet_name='Insights', index=False)
                    
                    metadata = {
                        'Report Generated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Number of Subscribers': len(selected_subscribers),
                        'Selection Mode': selection_mode,
                        'Variables Used': ", ".join(k for k, v in variables.items() if v)
                    }
                    metadata_df = pd.DataFrame(list(metadata.items()), columns=['Parameter', 'Value'])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                excel_data = buffer.getvalue()
                st.download_button(
                    "Download Complete Report",
                    excel_data,
                    f"MTN_Complete_Report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    "application/vnd.ms-excel",
                    key='download-complete',
                    on_click=lambda: None  # Prevents reload
                )
        
        # Insights tab
        with tabs[1]:
            st.subheader("Upsell & Cross-sell Insights")
            
            # Format and display the explanation text
            formatted_text = format_markdown_text(explanation_text.strip())
            st.markdown(formatted_text)
            
            # Extract and categorize bullet points
            bullets = extract_bullet_points(explanation_text)
            if bullets:
                # Categorize bullets
                upsell_bullets = []
                crosssell_bullets = []
                other_bullets = []
                
                for bullet in bullets:
                    if re.search(r'upsell|upgrade|higher|premium', bullet, re.IGNORECASE):
                        upsell_bullets.append(("Upsell", bullet))
                    elif re.search(r'cross.?sell|additional|complement|bundle', bullet, re.IGNORECASE):
                        crosssell_bullets.append(("Cross-sell", bullet))
                    else:
                        other_bullets.append(("Other", bullet))
                # Combine all categorized bullets
                categorized_bullets = upsell_bullets + crosssell_bullets + other_bullets
                
                # Create a dataframe
                details_df = pd.DataFrame(categorized_bullets, columns=["Type", "Strategy"])
                
                # Display as a table with improved styling
                st.subheader("Structured Insights")
                st.dataframe(
                    details_df.style.apply(
                        lambda x: ['background-color: rgba(209, 255, 214, 0.3)' if x['Type'] == 'Upsell' 
                                      else 'background-color: rgba(209, 240, 255, 0.3)' if x['Type'] == 'Cross-sell' 
                                      else '' for _ in x],  # Using rgba with transparency for better visibility
                        axis=1
                    ),
                    use_container_width=True
                )
                
                # Download button for insights - prevent reload
                csv = details_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Strategies CSV",
                    csv,
                    f"MTN_UpsellCrosssell_Strategies_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                    key='download-strategies',
                    on_click=lambda: None  # Prevents reload
                )
        
        # Comparison View tab
        with tabs[2]:
            st.subheader("Product Recommendation Comparison")
            
            # Create and display comparison chart
            fig = create_comparison_chart(table_df)
            if fig:
                st.pyplot(fig)
            else:
                st.warning("Could not create comparison chart. No data available.")
            
            # Display category distribution
            if table_df is not None:
                st.subheader("Category Distribution")
                category_counts = table_df['Category'].value_counts().reset_index()
                category_counts.columns = ['Category', 'Count']
                category_counts['Percentage'] = (category_counts['Count'] / category_counts['Count'].sum() * 100).round(2)
                category_counts['Percentage'] = category_counts['Percentage'].astype(str) + '%'
                
                st.dataframe(category_counts, use_container_width=True)
        
        # Raw Data tab
        with tabs[3]:
            st.subheader("Raw Subscriber Data")
            st.dataframe(subscriber_df, use_container_width=True)
            
            st.subheader("Product Catalogue")
            st.dataframe(product_df, use_container_width=True)
            
            st.subheader("Raw AI Response")
            st.text_area("Full AI Response", full_response, height=300)
    else:
        st.info("Run the analysis to see recommendations.")

if __name__ == "__main__":
    main()
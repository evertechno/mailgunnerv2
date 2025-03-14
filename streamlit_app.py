import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
from googletrans import Translator
import asyncio

# MJML API endpoint and key
MJML_API_URL = "https://api.mjml.io/v1/render"
MJML_APP_ID = st.secrets["MJML_APP_ID"]
MJML_SECRET_KEY = st.secrets["MJML_SECRET_KEY"]

# Function to check API key
def check_api_key(user_key):
    # List of allowed API keys stored in secrets
    valid_keys = [
        st.secrets["api_keys"].get("key_1"),
        st.secrets["api_keys"].get("key_2"),
        st.secrets["api_keys"].get("key_3"),
        st.secrets["api_keys"].get("key_4"),
        st.secrets["api_keys"].get("key_5")
    ]
    return user_key in valid_keys

# Function to send email using Mailgun
MAILGUN_DOMAIN = "evertechcms.in"
MAILGUN_FROM = "Ever CMS <mailgun@evertechcms.in>"

def send_email(to_email, subject, html, api_key):
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", api_key),
            data={"from": MAILGUN_FROM,
                  "to": to_email,
                  "subject": subject,
                  "html": html}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to send email to {to_email}: {e}")
        return False

# Function to generate structured content using Gemini
def generate_structured_content(prompt):
    try:
        pre_prompt = "Please provide elaborative, concise, and structured content based on the input below. Do not ask any questions or request additional information. Your response should be complete and directly address the given prompt."
        full_prompt = pre_prompt + "\n" + prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        cleaned_text = response.text.replace("***", "").replace("##", "").replace("<<", "").replace(">>", "").replace("~~", "").replace("* **", "").replace("* ", "").replace("Subject:", "").replace("*", "").strip()
        return cleaned_text
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return None

# Function to generate email body based on template, topic, and personalization
def generate_email_body(template, topic, first_name, personalization_data):
    prompt = f"Generate a {template} email body about {topic}, addressing the recipient as Dear {first_name}."
    for key, value in personalization_data.items():
        prompt += f" Include {key}: {value}."
    return generate_structured_content(prompt)

# Function to render MJML to HTML using MJML API
def render_mjml(mjml_content):
    try:
        response = requests.post(
            MJML_API_URL,
            auth=(MJML_APP_ID, MJML_SECRET_KEY),
            json={"mjml": mjml_content}
        )
        response.raise_for_status()
        return response.json()["html"]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to render MJML: {e}")
        return None

# Function for Multilingual Support using Google Translate (Asynchronous)
async def translate_text(text, target_language):
    translator = Translator()
    try:
        translation = await translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        st.error(f"Error translating text: {e}")
        return text

# Streamlit app for API key authorization
user_key = st.text_input("Enter your API key to access the app:", type="password")

# Add custom CSS to hide the header and the top-right buttons
hide_streamlit_style = """
    <style>
        .css-1r6p8d1 {display: none;} /* Hides the Streamlit logo in the top left */
        .css-1v3t3fg {display: none;} /* Hides the star button */
        .css-1r6p8d1 .st-ae {display: none;} /* Hides the Streamlit logo */
        header {visibility: hidden;} /* Hides the header */
        .css-1tqja98 {visibility: hidden;} /* Hides the header bar */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if user_key:
    if not check_api_key(user_key):
        st.error("Invalid API Key! Access Denied.")
    else:
        # Proceed with the application if the API key is valid
        st.title("AI Powered Newsletter & Email Automation")

        st.header("Email Campaign Creation")

        # Custom CSS for enhanced UI and animation
        hide_streamlit_style = """
            <style>
                .css-1r6p8d1 {display: none;} /* Hide Streamlit logo */
                .css-1v3t3fg {display: none;} /* Hide star button */
                header {visibility: hidden;} /* Hide header */
                .css-1tqja98 {visibility: hidden;} /* Hide header bar */
                body {background-color: #f4f4f9;} /* Set background color */
                .stButton button {background-color: #4CAF50; color: white;} /* Green buttons */
                .stTextArea {border-radius: 8px;} /* Rounded text areas */
                .stSelectbox {border-radius: 8px;} /* Rounded selectboxes */
                .stCheckbox {margin-bottom: 15px;} /* Space between checkboxes */
                
                /* Animation CSS */
                @keyframes fadeIn {
                    0% { opacity: 0; }
                    100% { opacity: 1; }
                }
                .fade-in {
                    animation: fadeIn 1s ease-in-out;
                }
            </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload CSV file (columns: email, first_name)", type="csv")

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'email' not in df.columns or 'first_name' not in df.columns:
                    st.error("CSV must contain 'email' and 'first_name' columns.")
                else:
                    email_list = df['email'].tolist()
                    first_name_list = df['first_name'].tolist()

                    subject = st.text_input("Email Subject", "Your Newsletter")
                    topic = st.text_input("Email Content Topic", "Latest AI Trends")

                    # Template selection with new templates and design options
                    template_options = ["Simple", "Professional", "Marketing", "Announcement", "Update", "Personalized", "Event Invite", "Seasonal Offer"]
                    selected_template = st.selectbox("Select Email Template", template_options)

                    email_templates = {
                        "Simple": "<mjml><mj-body><mj-section><mj-column><mj-text>Dear {first_name},</mj-text><mj-text>We have exciting news to share with you. Stay tuned for updates!</mj-text><mj-text>Best regards,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>",
                        "Professional": "<mjml><mj-body><mj-section><mj-column><mj-text>Dear {first_name},</mj-text><mj-text>I hope this email finds you well. We would like to inform you about some recent developments.</mj-text><mj-text>Sincerely,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>",
                        "Marketing": "<mjml><mj-body><mj-section><mj-column><mj-text>Hi {first_name},</mj-text><mj-text>Check out our new offerings! Don't miss out on special discounts just for you.</mj-text><mj-text>Best,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>",
                        "Announcement": "<mjml><mj-body><mj-section><mj-column><mj-text>Dear {first_name},</mj-text><mj-text>We're thrilled to announce our new product. Take a look at what we've prepared for you!</mj-text><mj-text>Best regards,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>",
                        "Update": "<mjml><mj-body><mj-section><mj-column><mj-text>Dear {first_name},</mj-text><mj-text>Here's your latest update. Make sure you stay up-to-date with all the new changes!</mj-text><mj-text>Best regards,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>",
                        "Personalized": "<mjml><mj-body><mj-section><mj-column><mj-text>Dear {first_name},</mj-text><mj-text>We're reaching out to provide an exclusive offer tailored just for you. Enjoy a special deal today!</mj-text><mj-text>Best,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>",
                        "Event Invite": "<mjml><mj-body><mj-section><mj-column><mj-text>Dear {first_name},</mj-text><mj-text>You're invited to an exclusive event! Don't miss out on this amazing opportunity.</mj-text><mj-text>Looking forward to seeing you there!<br>Best regards,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>",
                        "Seasonal Offer": "<mjml><mj-body><mj-section><mj-column><mj-text>Dear {first_name},</mj-text><mj-text>Season's Greetings! We have an exclusive holiday offer for you. Grab it before it's gone!</mj-text><mj-text>Warm regards,<br>Your Company</mj-text></mj-column></mj-section></mj-body></mjml>"
                    }
                    template_preview = st.selectbox("Select Template Preview", list(email_templates.keys()))
                    st.text_area("Template Preview", email_templates[template_preview].format(first_name="John"))

                    # Language selection
                    language_options = ["en", "es", "fr", "de", "it", "pt", "ru", "hi"]  # Added Hindi
                    selected_language = st.selectbox("Select Email Language", language_options)

                    # Theme selection
                    theme_options = ["Default", "Modern", "Classic", "Minimalist"]
                    selected_theme = st.selectbox("Select Email Theme", theme_options)

                    # Personalization inputs
                    personalization_data = {}
                    if selected_template == "Personalized":
                        personalization_data["Company Name"] = st.text_input("Enter Company Name", "Ever Tech")
                        personalization_data["Product Name"] = st.text_input("Enter Product Name", "AI Newsletter Tool")
                        personalization_data["Offer"] = st.text_input("Enter Offer", "Free Trial")

                    if st.button("Generate Email Body"):
                        if len(email_list) > 0:
                            generated_body = generate_email_body(selected_template, topic, first_name_list[0], personalization_data)
                            if generated_body:
                                st.session_state.email_body = generated_body
                            else:
                                st.error("Failed to generate email body.")
                        else:
                            st.error("Please upload a CSV file first.")

                    if 'email_body' not in st.session_state:
                        st.session_state.email_body = ""

                    email_body = st.text_area("Email Body", st.session_state.email_body, height=300)

                    # Update the session state with the new value
                    st.session_state.email_body = email_body

                    # Translate email content if needed
                    if selected_language != "en":
                        # Asynchronous translation
                        translated_body = asyncio.run(translate_text(email_body, selected_language))
                        st.session_state.translated_body = translated_body  # Store the translated body in session state

                    # Show the translated body if available
                    if 'translated_body' in st.session_state:
                        st.text_area("Translated Email Body", st.session_state.translated_body, height=300)

                    preview_email = st.checkbox("Preview Email with First Record")
                    if preview_email and len(email_list) > 0:
                        preview_text = st.session_state.translated_body if 'translated_body' in st.session_state else email_body
                        preview_text = preview_text.format(first_name=first_name_list[0])
                        st.write("Preview:")
                        st.write(preview_text)

                    confirm_send = st.checkbox("Confirm and Send Campaign")

                    if confirm_send and st.button("Send Emails"):
                        api_key = st.secrets["MAILGUN_API_KEY"]
                        success_count = 0
                        failure_count = 0
                        for email, first_name in zip(email_list, first_name_list):
                            personalized_body = st.session_state.translated_body if 'translated_body' in st.session_state else email_body
                            personalized_body = personalized_body.format(first_name=first_name)
                            mjml_content = email_templates[selected_template].format(first_name=first_name)
                            html_content = render_mjml(mjml_content)
                            if html_content and send_email(email, subject, html_content, api_key):
                                success_count += 1
                            else:
                                failure_count += 1

                        st.success(f"Emails sent successfully: {success_count}")
                        if failure_count > 0:
                            st.warning(f"Emails failed to send: {failure_count}")

            except Exception as e:
                st.error(f"Error processing CSV: {e}")

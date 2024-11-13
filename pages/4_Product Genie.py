import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
from datetime import datetime

def init_page():
    st.set_page_config(page_title="Product Analysis & Instagram Post Generator", layout="wide")
    
    st.markdown("""
        <style>
        /* Main background color */
        .stApp {
            background-color: #81334C;
            color: white;
        }

        /* Adjust text colors for better visibility on dark background */
        h1, h2, h3 {
            color: white !important;
        }

        p {
            color: white;
        }

        /* Container styling */
        .post-container {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }

        .post-header {
            font-weight: bold;
            margin-bottom: 10px;
            color: white;
        }

        .hashtag {
            color: #FFB6C1;
            font-weight: 500;
        }

        .cta-button {
            background-color: #0095f6;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin: 10px 0;
        }

        /* Style Streamlit elements */
        .stTextInput > div > div > input {
            color: white;
            background-color: rgba(255, 255, 255, 0.1);
        }

        .stButton>button {
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .stButton>button:hover {
            background-color: rgba(255, 255, 255, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)

def analyze_product(image, model):
    """Analyze product image using Gemini"""
    try:
        analysis_prompt = """
        You are a product analysis AI. Look at this image and provide the following information in JSON format:
        {
            "product_name": "",
            "category": "",
            "key_features": [],
            "target_market": "",
            "price_range": ""
        }

        Make sure to:
        1. Be specific about product details
        2. List at least 3-5 key features
        3. Identify clear target market
        4. Provide realistic price range
        """
        
        response = model.generate_content([image, analysis_prompt])
        return json.loads(response.text)
    except Exception as e:
        raise Exception(f"Analysis error: {str(e)}")

def generate_instagram_content(product_data, model):
    """Generate Instagram post content using Gemini"""
    try:
        prompt = f"""
        You are a social media expert. Create an engaging Instagram post for this product:
        Product Details: {json.dumps(product_data)}
        
        Respond in this exact JSON format:
        {{
            "caption": "Write engaging caption here (max 200 chars)",
            "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
            "call_to_action": "Write compelling CTA here"
        }}

        Guidelines:
        1. Caption should be catchy and benefit-focused
        2. Hashtags should be relevant and trending
        3. Call to action should drive engagement
        4. Use appropriate emoji in caption
        """
        
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        raise Exception(f"Content generation error: {str(e)}")

def display_instagram_preview(image, content):
    """Display Instagram post preview"""
    try:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, use_container_width=True)
        
        with col2:
            st.markdown("### ✍️ Caption")
            st.write(content["caption"])
            
            st.markdown("### 🏷️ Hashtags")
            for hashtag in content["hashtags"]:
                st.markdown(f"#{hashtag}")
            
            st.markdown("### 🎯 Call to Action")
            st.info(content["call_to_action"])
            
            # Download button
            post_content = f"""
            📝 Caption:
            {content['caption']}
            
            🏷️ Hashtags:
            {' '.join(['#' + tag for tag in content['hashtags']])}
            
            🎯 Call to Action:
            {content['call_to_action']}
            """
            
            st.download_button(
                label="📥 Download Post Content",
                data=post_content,
                file_name=f"instagram_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    except Exception as e:
        st.error(f"Error displaying preview: {str(e)}")

def main():
    init_page()
    
       
    st.markdown("<h1 style='text-align: center;'> 🛍️ Product Analysis & Instagram Post Generator </h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'> Upload a product image to get AI-generated analysis and Instagram post content </h4>", unsafe_allow_html=True)    
    
    # API key input
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    
    if api_key:
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # File upload
            uploaded_file = st.file_uploader("Upload product image", type=['jpg', 'jpeg', 'png'])
            
            if uploaded_file:
                try:
                    # Display uploaded image
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Product", use_container_width=True)
                    
                    # Product analysis button
                    if st.button("✨ Analyze Product & Generate Post"):
                        with st.spinner("🔍 Analyzing image and generating content..."):
                            try:
                                # Generate product analysis
                                st.subheader("📊 Product Analysis")
                                product_data = analyze_product(image, model)
                                
                                # Display analysis in a cleaner format
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Product Name:**", product_data["product_name"])
                                    st.write("**Category:**", product_data["category"])
                                    st.write("**Price Range:**", product_data["price_range"])
                                with col2:
                                    st.write("**Target Market:**", product_data["target_market"])
                                    st.write("**Key Features:**")
                                    for feature in product_data["key_features"]:
                                        st.write(f"• {feature}")
                                
                                # Generate and display Instagram post
                                st.markdown("---")
                                st.subheader("📱 Instagram Post Preview")
                                insta_content = generate_instagram_content(product_data, model)
                                
                                if insta_content:
                                    display_instagram_preview(image, insta_content)
                                
                            except Exception as e:
                                st.error(f"Analysis Error: {str(e)}")
                                st.write("Please try again or check your API key.")
                                
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    
        except Exception as e:
            st.error(f"Error configuring API: {str(e)}")
    else:
        st.info("👋 Please enter your Gemini API key to start.")
    
    # Sidebar tips
    st.sidebar.markdown("""
    ### 💡 Tips for Best Results
    
    **📸 Image Quality:**
    - Use clear, well-lit photos
    - Show product from best angle
    - Include key details in frame
    
    **📝 Content Tips:**
    - Keep captions engaging
    - Use trending hashtags
    - Add clear call-to-action
    
    **⏰ Best Posting Times:**
    - Weekdays: 11 AM - 2 PM
    - Weekends: 10 AM - 11 AM
    """)

if __name__ == "__main__":
    main()

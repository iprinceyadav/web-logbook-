import streamlit as st
import os

# Display the banner image at the top, full width
if os.path.exists('landing/banner3.png'):
    st.image('landing/banner3.png', use_container_width=True)
else:
    st.warning("Image not found at landing/banner3.png")

# ... rest of your app code ...
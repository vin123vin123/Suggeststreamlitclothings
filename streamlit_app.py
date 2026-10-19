import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Multi-API Clothing Store",
    page_icon="🛍️",
    layout="wide"
)

# 2. Define Free API Sources & Links
API_SOURCES = {
    "Fake Store API": {
        "url": "https://fakestoreapi.com clothing",
        "link": "https://fakestoreapi.com",
        "description": "A free online REST API for e-commerce testing. We pull men's and women's clothing from here."
    },
    "Platzi Fake Store API": {
        "url": "https://escuelajs.co",
        "link": "https://platzi.com",
        "description": "Real e-commerce data with high-quality fashion product images and clean JSON outputs."
    }
}

# 3. Main Header & Banner
st.title("👗 Multi-API Digital Clothing Boutique")
st.write("Welcome to the aggregate clothing hub powered concurrently by independent free data platforms.")

# 4. API Directory Layout (Directly on the Home Page)
st.markdown("### 🔗 Direct API Documentation Links")
api_cols = st.columns(2)

for idx, (name, info) in enumerate(API_SOURCES.items()):
    with api_cols[idx]:
        with st.container(border=True):
            st.markdown(f"#### **[{name}]({info['link']})**")
            st.write(info['description'])
            st.caption(f"Endpoint: `{info['url']}`")

st.markdown("---")

# 5. Native Page Filter Selection
st.markdown("### 🗂️ Explore Collections")
app_mode = st.segmented_control(
    "Choose a Store Section:", 
    options=["All Clothing", "Fake Store API Inventory", "Platzi Fashion API Inventory"],
    default="All Clothing"
)

# 6. Data Fetching Functions (Cached for performance)
@st.cache_data(ttl=600)
def fetch_fake_store_data():
    try:
        men_res = requests.get("https://fakestoreapi.com clothing", timeout=10)
        women_res = requests.get("https://fakestoreapi.comproducts/category/women's clothing", timeout=10)
        
        products = []
        if men_res.status_code == 200:
            products.extend(men_res.json())
        if women_res.status_code == 200:
            products.extend(women_res.json())
        return products
    except Exception as e:
        st.error(f"Error connecting to Fake Store API: {e}")
        return []

@st.cache_data(ttl=600)
def fetch_platzi_data():
    try:
        res = requests.get("https://escuelajs.co", timeout=10)
        if res.status_code == 200:
            all_items = res.json()
            clothing_items = [
                item for item in all_items 
                if item.get('category', {}).get('name') in ['Clothes', 'Shoes', 'Miscellaneous']
            ][:12]
            return clothing_items
        return []
    except Exception as e:
        st.error(f"Error connecting to Platzi API: {e}")
        return []

# 7. UI Grid Rendering Helper
def render_product_grid(products, source_type):
    if not products:
        st.warning("No products found or API is currently unreachable.")
        return

    cols = st.columns(3)
    for i, item in enumerate(products):
        with cols[i % 3]:
            # Normalize fields across different APIs
            if source_type == "fakestore":
                title = item.get('title', 'Unknown Item')
                price = item.get('price', 0.0)
                image_url = item.get('image', '')
                desc = item.get('description', '')[:100] + "..."
            else: # platzi
                title = item.get('title', 'Unknown Item')
                price = item.get('price', 0.0)
                images = item.get('images', [])
                image_url = images[0] if isinstance(images, list) and images else images
                if isinstance(image_url, str) and (image_url.startswith('["') or image_url.startswith('[')):
                    image_url = image_url.replace('["', '').replace('"]', '').replace('[', '').replace(']', '')
                desc = item.get('description', '')[:100] + "..."

            with st.container(border=True):
                if image_url:
                    st.image(image_url, use_container_width=True)
                else:
                    st.image("https://placehold.co", use_container_width=True)
                
                st.subheader(f"{title[:40]}")
                st.markdown(f"### **\${price}**")
                st.caption(desc)
                
                if st.button("Add to Cart", key=f"btn_{source_type}_{item.get('id')}_{i}"):
                    st.success(f"Added {title[:20]}... to cart!")

# 8. Rendering Content Grid
fake_store_products = fetch_fake_store_data()
platzi_products = fetch_platzi_data()

if app_mode == "All Clothing":
    st.markdown("### 🏷️ From: Fake Store API Section")
    render_product_grid(fake_store_products[:6], "fakestore")
    
    st.markdown("---")
    
    st.markdown("### 🏷️ From: Platzi Fashion API Section")
    render_product_grid(platzi_products[:6], "platzi")

elif app_mode == "Fake Store API Inventory":
    st.markdown("## 🛒 Fake Store API Exclusive Feed")
    render_product_grid(fake_store_products, "fakestore")

elif app_mode == "Platzi Fashion API Inventory":
    st.markdown("## 👟 Platzi API Exclusive Feed")
    render_product_grid(platzi_products, "platzi")

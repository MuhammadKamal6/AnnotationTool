import os
import pandas as pd
import streamlit as st
from PIL import Image
from pathlib import Path
from datetime import datetime

# === CONFIGURATION ===
IMAGE_ROOT = r"G:\My Drive\smallcopy"  # <-- Update to your local Drive-synced folder
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

st.set_page_config(page_title="Secure Annotation Tool", layout="centered")
st.title("🔐 Pedestrian Annotation Tool")

# === LOGIN ===
annotator = st.text_input("Enter your name:")
if not annotator:
    st.stop()

# Clean annotator name for filename
username_clean = annotator.strip().lower().replace(" ", "_")
user_csv_path = os.path.join(LOG_DIR, f"{username_clean}.csv")

# === LOAD IMAGES ===
@st.cache_data
def load_images():
    return sorted(Path(IMAGE_ROOT).rglob("frame_*.png"))

images = load_images()
if not images:
    st.error("❌ No frame_*.png images found.")
    st.stop()

if "index" not in st.session_state:
    st.session_state.index = 0

# === HANDLE END ===
if st.session_state.index >= len(images):
    st.success("✅ All frames annotated.")
    st.stop()

# === CURRENT IMAGE ===
img_path = images[st.session_state.index]
ped_id = img_path.parent.name
scenario = img_path.parent.parent.name
frame_number = int(img_path.stem.split("_")[1])

# === SHOW IMAGE ===
st.image(Image.open(img_path).resize((480, 480)), clamp=True, use_container_width=False)
st.markdown(f"**Scenario:** `{scenario}`&nbsp;&nbsp; | &nbsp;&nbsp;**Pedestrian:** `{ped_id}`&nbsp;&nbsp; | &nbsp;&nbsp;**Frame:** `{img_path.name}`")

# === FORM ===
with st.form("annotation_form"):
    age = st.radio("Age", ["child", "adult", "senior"])
    gender = st.radio("Gender", ["male", "female"])
    crossing = st.radio("Crossing", ["Crossing", "not Crossing"])
    visibility = st.radio("Cross Walk Condition", ["N/N", "High visible", "Partially visible", "Not visible"])
    submit = st.form_submit_button("✅ Submit Annotation")

# === SAVE ===
if submit:
    record = {
        "Annotator": annotator,
        "Timestamp": str(datetime.now()),
        "Pedestrian ID": ped_id,
        "Scenario Number": scenario,
        "Frame Number": frame_number,
        "Age": age,
        "Gender": gender,
        "Crossing or not Crossing": crossing,
        "Cross Walk Condition": visibility,
        "Nearest Crossing Location": ""
    }

    # Append to the annotator's CSV file
    df = pd.DataFrame([record])
    if os.path.exists(user_csv_path):
        df.to_csv(user_csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(user_csv_path, mode='w', header=True, index=False)

    st.session_state.index += 1
    st.rerun()

# === Progress
st.markdown(f"🖼️ Frame `{st.session_state.index + 1}` of `{len(images)}`")


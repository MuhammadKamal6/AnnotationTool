import os
import json
import pandas as pd
import streamlit as st
from PIL import Image
from pathlib import Path

# === CONFIGURATION ===
IMAGE_ROOT = "https://drive.google.com/drive/folders/1mmXY0U10upZ3aeQcfY7Ija2AIOH84HYv?usp=sharing"  # your synced folder
EXPORT_CSV = "all_annotations.csv"

# === Load all image paths
@st.cache_data
def load_images():
    return sorted(Path(IMAGE_ROOT).rglob("frame_*.png"))

images = load_images()
if not images:
    st.error("No images found.")
    st.stop()

# === Session state
if "index" not in st.session_state:
    st.session_state.index = 0
if "annotations" not in st.session_state:
    st.session_state.annotations = []

# === Current frame
current_img_path = images[st.session_state.index]
pedestrian_id = current_img_path.parent.name
scenario = current_img_path.parent.parent.name
frame_name = current_img_path.name
frame_number = int(frame_name.split('_')[1].split('.')[0])

# === UI
st.title("🚶‍♀️ Pedestrian Annotation Tool")
st.markdown(f"**Scenario:** `{scenario}` &nbsp;&nbsp; **Pedestrian ID:** `{pedestrian_id}` &nbsp;&nbsp; **Frame:** `{frame_name}`")

# === Display image
image = Image.open(current_img_path).resize((480, 480))
st.image(image)

# === Form
with st.form("annotation_form"):
    age = st.radio("Age", ["child", "adult", "senior"])
    gender = st.radio("Gender", ["male", "female"])
    crossing = st.radio("Crossing", ["Crossing", "not Crossing"])
    condition = st.radio("Cross Walk Condition", ["N/N", "High visible", "Partially visible", "Not visible"])

    submit = st.form_submit_button("Submit & Next")

# === Save
if submit:
    annotation = {
        "Pedestrian ID": pedestrian_id,
        "Scenario Number": scenario,
        "Frame Number": frame_number,
        "Age": age,
        "Gender": gender,
        "Crossing or not Crossing": crossing,
        "Cross Walk Condition": condition,
        "Nearest Crossing Location": ""
    }

    # Save JSON per frame
    json_path = current_img_path.with_suffix('.json')
    with open(json_path, "w") as f:
        json.dump(annotation, f, indent=4)

    # Optional CSV log
    st.session_state.annotations.append(annotation)

    # Advance
    st.session_state.index += 1
    if st.session_state.index >= len(images):
        st.success("All frames annotated!")
        st.session_state.index = 0

    st.experimental_rerun()

# Export CSV button
if st.button("📤 Export All Annotations"):
    if st.session_state.annotations:
        pd.DataFrame(st.session_state.annotations).to_csv(EXPORT_CSV, index=False)
        st.success(f"Exported to {EXPORT_CSV}")
    else:
        st.warning("No annotations to export.")

# Progress
st.markdown(f"Frame `{st.session_state.index + 1}` of `{len(images)}`")


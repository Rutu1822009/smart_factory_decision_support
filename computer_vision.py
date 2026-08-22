import streamlit as st
from PIL import Image
from ultralytics import YOLO


@st.cache_resource
def load_model():
    return YOLO("yolo11n.pt")


model = load_model()


def computer_vision_page():

    st.title("📷 Computer Vision - Visual Inspection")

    st.write(
        "Upload a product image to perform Computer Vision inspection."
    )

    uploaded_file = st.file_uploader(
        "Upload Product Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.subheader("Uploaded Image")
        st.image(
            image,
            caption="Product Image",
            use_container_width=True
        )

        if st.button("🔍 Analyze Image"):

            with st.spinner("Analyzing image..."):

                results = model(image)

            st.subheader("🔎 Detection Result")

            result_image = results[0].plot()

            st.image(
                result_image,
                caption="Computer Vision Detection",
                use_container_width=True
            )

            detections = results[0].boxes

            if detections is not None and len(detections) > 0:

                st.success(
                    f"✅ {len(detections)} object(s) detected."
                )

                st.subheader("Detected Objects")

                for box in detections:

                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])

                    class_name = model.names[class_id]

                    st.write(
                        f"• **{class_name}** — "
                        f"Confidence: **{confidence * 100:.1f}%**"
                    )

            else:

                st.info("No object detected in the image.")
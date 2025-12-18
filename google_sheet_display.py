import streamlit as st
import pandas as pd
import requests
from io import StringIO


N8N_WEBHOOK_URL = "https://emeraldlabs.app.n8n.cloud/webhook/invoice-upload-image"

st.set_page_config(page_title="Manor Bill Upload", layout="wide")

# Powder-blue / powder-pink / white stripes
striped_bg_css = """
<style>
[data-testid="stAppViewContainer"] {
    background: repeating-linear-gradient(
        90deg,                /* direction of stripes */
        #B3D9FF 0px,          /* light blue */
        #B3D9FF 120px,
        #FFD1E8 120px,        /* light pink */
        #FFD1E8 240px,
        #FFFFFF 240px,        /* white */
        #FFFFFF 360px
    );
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0); /* transparent header */
}

[data-testid="stToolbar"] {
    background: rgba(0,0,0,0);
}
</style>
"""

st.markdown(striped_bg_css, unsafe_allow_html=True)

st.title("Manor Bill Upload 📊")
st.write(
    "Upload an image and convert it into an excel sheet that you can download."
)

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "heic", "webp"],
    accept_multiple_files=False,
)

if uploaded_file and st.button("Convert to sheet"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

    r = requests.post(N8N_WEBHOOK_URL, files=files, timeout=60)

    # st.write("n8n status:", r.status_code)
    # st.write(r.text)
    r.raise_for_status()

    csv_text = r.text.strip()                 # remove leading/trailing whitespace/newlines
    csv_text = csv_text.rstrip('"\', \n\r\t') # remove stray trailing quote/comma/backslash etc.
    df = pd.read_csv(StringIO(csv_text))

    st.session_state["df"] = df
    st.session_state["original_filename"] = "image_extracted.csv"
    #st.success("CSV loaded into dataframe!")


if "df" in st.session_state:
    #st.success(f"Loaded file: **{st.session_state['original_filename']}**")

    st.write("### Edit your sheet")

    # 2. Editable table (you can change cells, add/delete rows, etc.)
    edited_df = st.data_editor(
        st.session_state["df"],
        use_container_width=True,
        num_rows="dynamic",  # allows adding new rows
        key="data_editor",
    )

    # 3. Save button: update session_state with edits
    if st.button("Save changes"):
        st.session_state["df"] = edited_df
        st.toast("Changes saved to session ✔️")

        # 🔁 ALSO send edited sheet to n8n as CSV
        csv_for_n8n = edited_df.to_csv(index=False).encode("utf-8")
        files = {
            "file": ("manor_bill_edited.csv", csv_for_n8n, "text/csv"),
        }

    # 4. Download edited version as CSV
    st.write("### Download edited file")

    csv_data = st.session_state["df"].to_csv(index=False).encode("utf-8")
    default_name = (
        st.session_state.get("original_filename", "edited_sheet.csv")
        .rsplit(".", 1)[0]
        + "_edited.csv"
    )

    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_data,          # ✅ just the bytes
        file_name=default_name,
        mime="text/csv",
    )

    # Optional info
    # st.write("### Basic info")
    # st.write(f"- Rows: {st.session_state['df'].shape[0]}")
    # st.write(f"- Columns: {st.session_state['df'].shape[1]}")
    # st.write("#### Column names")
    # st.write(list(st.session_state["df"].columns))
else:
    st.info("👆 Upload an image to get started.")


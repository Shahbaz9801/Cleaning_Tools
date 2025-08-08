import streamlit as st
from your_cleaning_script import NoonCleaner, AmazonCleaner, RevibeCleaner, TalabatCleaner, CareemCleaner  # Import your class from your main code
import os

st.title("Sales Data Cleaning Tool")

option = st.selectbox("Choose Marketplace", ["Noon", "Amazon", "Revibe", "Talabat", "Careem"])

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    st.success("File uploaded successfully!")

    if st.button("Clean Data"):
        if option == "Noon":
            cleaner = NoonCleaner(uploaded_file)
            cleaner.clean()
            output_path = "Cleaned_" + option + "_Data.xlsx"
            cleaner.save_data(output_path)
            st.success("Data Cleaned Successfully!")
            with open(output_path, "rb") as f:
                st.download_button("Download Cleaned File", f, file_name=output_path)
        elif option == 'Amazon':
            # Step 1: Uploaded file ko temp folder me save karo
            temp_input_path = os.path.join(os.getcwd(), uploaded_file.name)
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
            # Step 2: Cleaner me temp file ka path do
            cleaner = AmazonCleaner(temp_input_path)
            cleaner.clean()
        
            # Step 3: Output file bhi temp me save karo
            output_path = os.path.join(os.getcwd(), f"Cleaned_{option}_Data.xlsx")
            cleaner.save_data(output_path)
        
            st.success("Data Cleaned Successfully!")
        
            # Step 4: Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    "Download Cleaned File",
                    data=f,
                    file_name=f"Cleaned_{option}_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        elif option == 'Revibe':
            cleaner = RevibeCleaner(uploaded_file)
            cleaner.clean()
            output_path = "Cleaned_" + option + "_Data.xlsx"
            cleaner.save_data(output_path)
            st.success("Data Cleaned Successfully!")
            with open(output_path, "rb") as f:
                st.download_button("Download Cleaned File", f, file_name=output_path)

        elif option == 'Talabat':
            cleaner = TalabatCleaner(uploaded_file)
            cleaner.clean()
            output_path = "Cleaned_" + option + "_Data.xlsx"
            cleaner.save_data(output_path)
            st.success("Data Cleaned Successfully!")
            with open(output_path, "rb") as f:
                st.download_button("Download Cleaned File", f, file_name=output_path)

        elif option == 'Careem':
            cleaner = CareemCleaner(uploaded_file)
            cleaner.clean()
            output_path = "Cleaned_" + option + "_Data.xlsx"
            cleaner.save_data(output_path)
            st.success("Data Cleaned Successfully!")
            with open(output_path, "rb") as f:
                st.download_button("Download Cleaned File", f, file_name=output_path)
        else:
            st.warning(f"{option} cleaning not yet implemented.")




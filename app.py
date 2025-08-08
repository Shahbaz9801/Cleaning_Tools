import streamlit as st
from your_cleaning_script import NoonCleaner, AmazonCleaner, RevibeCleaner, TalabatCleaner, CareemCleaner  # Import your class from your main code

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
            #sheet_name = ["100 MPH", "100_Miles", "Wishcare"]
            cleaner = AmazonCleaner(uploaded_file)
            cleaner.clean()
            output_path = "Cleaned_" + option + "_Data.xlsx"
            cleaner.save_data(output_path)
            st.success("Data Cleaned Successfully!")
            with open(output_path, "rb") as f:
                st.download_button("Download Cleaned File", f, file_name=output_path)

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


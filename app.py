import streamlit as st
from your_cleaning_script import NoonCleaner, AmazonCleaner, RevibeCleaner, TalabatCleaner, CareemCleaner  # Import your class from your main code
import os
import tempfile

st.set_page_config(page_title="Cleaning Toos", layout="centered")
st.title("Sales Data Cleaning Tool")

option = st.selectbox("Choose Marketplace", ["Noon", "Amazon", "Revibe", "Talabat", "Careem"])

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    st.success("File upload successfully!")

    if st.button("Clean Data"):
        #------------------------------------------------------------Noon Section--------------------------------------------------------------------------------
        if option == "Noon":
            # # Step 1: Temp input file save
            # with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_input:
            #     tmp_input.write(uploaded_file.getbuffer())
            #     temp_input_path = tmp_input.name
            file_ext = os.path.splitext(uploaded_file.name)[1]  # original extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_input:
                tmp_input.write(uploaded_file.getbuffer())
                temp_input_path = tmp_input.name

            
            # Step 2: Clean file
            cleaner = NoonCleaner(temp_input_path)
            cleaner.clean()
            
            # Step 3: Output file save
            output_fd, output_path = tempfile.mkstemp(suffix=".xlsx")
            os.close(output_fd)  # close handle, warna Windows block karega
            cleaner.save_data(output_path)

            # Step 4: Data preview before download
            st.subheader("Preview of Cleaned Data")
            st.dataframe(cleaner.data) 
            
            st.success("Data Cleaned Successfully!")
            
            # Step 5: Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Cleaned File",
                    data=f,
                    file_name="Cleaned_Noon_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            
        #------------------------------------------------------------Amazon Section--------------------------------------------------------------------------------          
        elif option == 'Amazon':
            # Step 1: Temp input file save
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_input:
                tmp_input.write(uploaded_file.getbuffer())
                temp_input_path = tmp_input.name
            
            # Step 2: Clean file
            cleaner = AmazonCleaner(temp_input_path)
            cleaner.clean()
            
            # Step 3: Output file save
            output_fd, output_path = tempfile.mkstemp(suffix=".xlsx")
            os.close(output_fd)  # close handle, warna Windows block karega
            cleaner.save_data(output_path)

            # Step 4: Data preview before download
            st.subheader("Preview of Cleaned Data")
            st.dataframe(cleaner.data)

            st.success("Data Cleaned Successfully!")
            
            # Step 5: Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Cleaned File",
                    data=f,
                    file_name="Cleaned_Amazon_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        

        
        #------------------------------------------------------------Revibe Section--------------------------------------------------------------------------------    
        elif option == 'Revibe':            # Step 1: Temp input file save
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_input:
                tmp_input.write(uploaded_file.getbuffer())
                temp_input_path = tmp_input.name
            
            # Step 2: Clean file
            cleaner = RevibeCleaner(temp_input_path)
            cleaner.clean()
            
            # Step 3: Output file save
            output_fd, output_path = tempfile.mkstemp(suffix=".xlsx")
            os.close(output_fd)  # close handle, warna Windows block karega
            cleaner.save_data(output_path)
            
            # Step 4: Data preview before download
            st.subheader("Preview of Cleaned Data")
            st.dataframe(cleaner.data)

            st.success("Data Cleaned Successfully!")
            
            # Step 5: Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Cleaned File",
                    data=f,
                    file_name="Cleaned_Revibe_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            

        #------------------------------------------------------------Talabat Section--------------------------------------------------------------------------------
        elif option == 'Talabat':
            cleaner = TalabatCleaner(uploaded_file)
            cleaner.clean()
            output_path = "Cleaned_" + option + "_Data.xlsx"
            cleaner.save_data(output_path)
            st.success("Data Cleaned Successfully!")
            with open(output_path, "rb") as f:
                st.download_button("Download Cleaned File", f, file_name=output_path)

        #------------------------------------------------------------Careem Section--------------------------------------------------------------------------------
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


















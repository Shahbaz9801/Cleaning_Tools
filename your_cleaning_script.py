import pandas as pd
import numpy as np
from dateutil import parser
master_df = pd.read_csv('product.csv')

class BaseCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def read_data(self):
        try:
            self.data = pd.read_csv(self.file_path)
            print(f"Data Loaded: {self.data.shape}")
        except Exception as e:
            print(f"Error Reading File: {e}")

    def save_data(self, output_file):
        try:
            self.data.to_excel(output_file, index=False)
            print(f"Data Saved to {output_file}")
        except Exception as e:
            print(f"Error Saving File: {e}")

    def convert_date(self, column_name):
        try:
            self.data[column_name] = pd.to_datetime(self.data[column_name])
        except Exception as e:
            print(f"Error Converting Date: {e}")

    def convert_date1(self, column_name):
        try:
            # Har row pe parser chalayenge jo mixed formats handle kare
            self.data[column_name] = self.data[column_name].apply(
                lambda x: parser.parse(str(x), dayfirst=True) if pd.notnull(x) else None
            )
        except Exception as e:
            print(f"Error Converting Date: {e}")

# Noon cleaner
class NoonCleaner(BaseCleaner):
    def clean(self):
        try:
            self.read_data()
            
            # Select and rename columns
            self.data = self.data[['order_timestamp','item_nr','sku','status','id_partner','country_code',
                                   'partner_sku','fulfillment_model','offer_price']]

            self.data = self.data.rename(columns={
                'order_timestamp':'Date',
                'item_nr':'Order Number',
                'sku':'SKU',
                'status':'Status',
                'id_partner':'Partner Id',
                'country_code':'Country',
                'partner_sku': 'Partner SKU',
                'fulfillment_model':'Fullfilment',
                'offer_price':'Sales_Price'
            })

            # Date conversion
            self.convert_date('Date')

            # Add Month, Month Number, Year
            self.data.insert(1, 'Month', self.data['Date'].dt.strftime('%B'))
            self.data.insert(2, 'Month Number', self.data['Date'].dt.month)
            self.data.insert(3, 'Year', self.data['Date'].dt.year)

            # Nub Partner
            self.data.insert(8, 'Nub Partner', self.data['Partner Id'].apply(self.get_nub_partner))

            self.data.insert(10,'Brand Name'," ")

            # Blank columns initialization
            self.data.insert(11,'Category'," ")
            self.data.insert(12,'Sub-Category'," ")
            self.data.insert(13,'Channel','Noon')
            self.data.insert(14,'Channel Item Name'," ")

            # Other columns
            self.data.insert(18, 'QTY', 1)
            self.data.insert(19, 'GMV', self.data['Sales_Price'] * self.data['QTY'])

            # Filter irrelevant statuses
            self.data = self.data[~self.data['Status'].isin([
                'Unshipped', 'Pending','Undelivered','Confirmed','Created','Exported','Fulfilling','Could Not Be Delivered','Processing'
            ])]

            # Replace Country / Status / Fulfilment values
            self.data['Country'] = self.data['Country'].replace({'SA':'Saudi', 'AE':'UAE'})
            self.data['Status'] = self.data['Status'].replace({'Shipped':'Delivered','CIR':'Cancelled'})
            self.data['Fullfilment'] = self.data['Fullfilment'].replace({'Fulfilled by Noon (FBN)':'FBN','Fulfilled by Partner (FBP)':'FBP'})

            # ===============================
            # ✅ FILL BLANKS FROM MASTER CSV
            # ===============================
            master_df = pd.read_csv('product.csv')
            # Clean SKU columns
            self.data['SKU'] = self.data['SKU'].astype(str).str.strip()
            master_df['SKU'] = master_df['SKU'].astype(str).str.strip()

            # Convert blanks to NaN
            self.data[['Brand Name','Category','Sub-Category','Channel Item Name']] = \
                self.data[['Brand Name','Category','Sub-Category','Channel Item Name']].replace(r'^\s*$', np.nan, regex=True)

            # Lookup merge (SKU basis)
            lookup = self.data[['SKU']].merge(
                master_df[['SKU','Brand','Category','Sub-Category','Product Titles']],
                on='SKU',
                how='left'
            )

            # Fill only blank values
            self.data['Brand Name'] = self.data['Brand Name'].fillna(lookup['Brand'])
            self.data['Category'] = self.data['Category'].fillna(lookup['Category'])
            self.data['Sub-Category'] = self.data['Sub-Category'].fillna(lookup['Sub-Category'])
            self.data['Channel Item Name'] = self.data['Channel Item Name'].fillna(lookup['Product Titles'])

            # ===============================
            # ✅ SET GMV = 0 WHERE STATUS IS CANCELLED
            # ===============================
            self.data.loc[self.data['Status']=='Cancelled', 'GMV'] = 0

            print(f"Cleaned Data Shape: {self.data.shape}")

        except Exception as e:
            print(f"Error Cleaning Noon Data: {e}")


    def get_nub_partner(self, pid):
        if pid in [46272, '46272']:
            return 'Nub-Partner 46272'
        elif pid in [181587, '181587']:
            return 'Nub-Partner 181587'
        elif pid in [47461, '47461']:
            return 'Nub-Partner 47461'
        elif pid in [74949, '74949']:
            return 'Nub-Partner 74949'
        else:
            return 'Null'


# Amazon Cleaner 
class AmazonCleaner(BaseCleaner):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.all_dataframes = []

    def read_data(self):
        try:
            # Sheet names detect karo
            xls = pd.ExcelFile(self.file_path, engine='openpyxl')
            available_sheets = xls.sheet_names

            if len(available_sheets) > 1:
                # Multiple sheet case
                for sheet in available_sheets:
                    df = pd.read_excel(self.file_path, sheet_name=sheet, engine='openpyxl')
                    df['Partner ID'] = sheet
                    df = df[df[df.columns[0]] != df.columns[0]]  # Remove duplicate header rows
                    self.all_dataframes.append(df)
                self.data = pd.concat(self.all_dataframes, ignore_index=True)
            else:
                # Single sheet case
                sheet = available_sheets[0]
                df = pd.read_excel(self.file_path, sheet_name=sheet, engine='openpyxl')
                df['Partner ID'] = sheet
                df = df[df[df.columns[0]] != df.columns[0]]  # Remove duplicate header rows
                self.data = df

            print(f"Amazon Sheets Read: {self.data.shape}")

        except Exception as e:
            print(f"Error Reading Amazon Sheets: {e}")


    def clean(self):
        try:
            self.read_data()
            self.data = self.data[['purchase-date','amazon-order-id','sku','item-status','Partner ID',
                                   'ship-country','sales-channel','product-name','asin',
                                   'fulfillment-channel','item-price','quantity']]

            self.data = self.data.rename(columns={
                'purchase-date': 'Date',
                'amazon-order-id': 'Order Number',
                'sku': 'SKU',
                'item-status': 'Status',
                'ship-country': 'Country',
                'sales-channel': 'Channel',
                'product-name': 'Channel Item Name',
                'asin': 'Partner SKU',
                'fulfillment-channel': 'Fulfillment',
                'item-price': 'Sales price',
                'quantity': 'QTY'
            })

            self.convert_date('Date')
            self.data['Date'] = pd.to_datetime(self.data['Date'].dt.date)

            self.data['Sales price'] = self.data['Sales price'].fillna(0)

            # Add Month, Month Number, Year
            self.data.insert(1, 'Month', self.data['Date'].dt.strftime('%B'))
            self.data.insert(2, 'Month Number', self.data['Date'].dt.month)
            self.data.insert(3, 'Year', self.data['Date'].dt.year)

            # Nub Partner and Brand
            self.data.insert(8, 'Nub Partner', self.data['Partner ID'].apply(self.get_nub_partner))
            self.data.insert(10, 'Brand Name', " ")
            self.data.insert(11, 'Category', " ")
            self.data.insert(12, 'Sub-Category', " ")

            # GMV
            self.data.insert(19, 'GMV', self.data['Sales price'] * self.data['QTY'])

            # Filter + Replace
            self.data = self.data[~self.data['Status'].isin([
                'Unshipped', 'Pending', 'Undelivered', 'Confirmed', 'Created', 'Exported', 'Fulfilling'
            ])]

            self.data['Country'] = self.data['Country'].replace({'SA': 'Saudi', 'AE': 'UAE', 'BH': 'Bahrain', 'KW': 'Kuwait', 'OM': 'Oman'})
            self.data['Channel'] = self.data['Channel'].replace({'Amazon.ae': 'Amazon','Amazon.sa':'Amazon'})
            self.data['Status'] = self.data['Status'].replace({'Shipped': 'Delivered'})
            self.data['Fulfillment'] = self.data['Fulfillment'].replace({'Amazon': 'FBA'})

            # ===============================
            # ✅ FILL BLANKS FROM MASTER CSV (SKU ↔ Partner SKU)
            # ===============================

            master_df = pd.read_csv('product.csv')

            # Clean columns
            self.data['SKU'] = self.data['SKU'].astype(str).str.strip()
            master_df['Partner SKU'] = master_df['Partner SKU'].astype(str).str.strip()

            # Convert blank strings to NaN
            cols = ['Brand Name', 'Category', 'Sub-Category']
            self.data[cols] = self.data[cols].replace(r'^\s*$', np.nan, regex=True)

            # 🔥 Lookup merge (SKU → Partner SKU)
            lookup = self.data[['SKU']].merge(
                master_df[['Partner SKU', 'Brand', 'Category', 'Sub-Category']],
                left_on='SKU',
                right_on='Partner SKU',
                how='left'
            )

            # Fill only blank values
            self.data['Brand Name'] = self.data['Brand Name'].fillna(lookup['Brand'])
            self.data['Category'] = self.data['Category'].fillna(lookup['Category'])
            self.data['Sub-Category'] = self.data['Sub-Category'].fillna(lookup['Sub-Category'])

            # ===============================
            # ✅ SET GMV = 0 WHERE STATUS IS CANCELLED
            # ===============================
            self.data.loc[self.data['Status']=='Cancelled', 'QTY'] = 1


            print(f"Cleaned Amazon Data Shape: {self.data.shape}")
        except Exception as e:
            print(f"Error Cleaning Amazon Data: {e}")


    def get_nub_partner(self, pid):
        if pid == 'Wishcare':
            return 'Nub-Partner Wishcare'
        elif pid == '100 MPH':
            return 'Nub-Partner 100 MPH'
        elif pid == '100_Miles':
            return 'Nub-Partner 100_Miles'
        else:
            return 'Null'


# Revibe Cleaner
class RevibeCleaner(BaseCleaner):
    def clean(self):
        try:
            self.read_data()

            # ✅ Step 1: Select Required Columns
            self.data = self.data[['Last Update Date', 'id', 'SKU (Old: Order Status)', 'Shipment Status',
                                   'Supplier', 'Country', 'Category', 'Condition', 'Model',
                                   'Variation: Color, Storage, Condition', 'Actual Cost']]

            # ✅ Step 2: Rename Columns for Standard Format
            self.data = self.data.rename(columns={
                'Last Update Date': 'Date',
                'id': 'Order Number',
                'SKU (Old: Order Status)': 'SKU',
                'Shipment Status': 'Status',
                'Supplier': 'Partner Id',
                'Condition': 'Sub-Category',
                'Actual Cost': 'Sales Price'
            })


            self.convert_date1('Date')
            # Ab Date column ko standard format me set kar do (YYYY-MM-DD HH:MM:SS)
            self.data['Date'] = pd.to_datetime(self.data['Date'])
            self.data['Date'] = pd.to_datetime(self.data['Date'].dt.date)

            # ✅ Step 4: Add Month, Month Number, Year Columns
            self.data.insert(1, 'Month', self.data['Date'].dt.strftime('%B'))
            self.data.insert(2, 'Month Number', self.data['Date'].dt.month)
            self.data.insert(3, 'Year', self.data['Date'].dt.year)

            # ✅ Step 5: Add Nub Partner, Brand, Channel, Fulfillment, QTY, GMV
            self.data.insert(8, 'Nub-Partner', 'Revibe ' + self.data['Partner Id'].astype(str))
            self.data.insert(10, 'Brand Name', 'Apple')
            self.data.insert(13, 'Channel', 'Revibe')
            self.data.insert(14, 'Channel Item Name', self.data['Model'] + ' ' + self.data['Variation: Color, Storage, Condition'])
            self.data.insert(15, 'Partner SKU', self.data['SKU'])
            self.data.insert(16, 'Fulfillment', 'FBR')
            self.data.insert(20, 'QTY', 1)
            self.data.insert(21, 'GMV', self.data['Sales Price'] * self.data['QTY'])

            # ✅ Step 6: Drop Unnecessary Columns
            self.data.drop(columns=['Model', 'Variation: Color, Storage, Condition'], inplace=True)

            # ✅ Step 7: Standardize Values
            self.data['Status'] = self.data['Status'].replace({
                'Shipped': 'Delivered',
                'At quality check': 'Delivered',
                'Refused delivery': 'Delivered'
            })
            self.data['Country'] = self.data['Country'].replace({'United Arab Emirates': 'UAE'})

            # ✅ Step 8: Sort by Date
            self.data = self.data.sort_values(by='Date', ascending=True)

            print(f"✅ Revibe Cleaned Data Shape: {self.data.shape}")
        except Exception as e:
            print(f"❌ Error Cleaning Revibe Data: {e}")

class TalabatCleaner(BaseCleaner):
    def clean(self):
        try:
            self.read_data()
            # TODO: Add Talabat specific cleaning logic
            print("Talabat cleaning not implemented yet.")
        except Exception as e:
            print(f"Error Cleaning Talabat Data: {e}")

class CareemCleaner(BaseCleaner):
    def clean(self):
        try:
            self.read_data()
            # TODO: Add Careem specific cleaning logic
            print("Careem cleaning not implemented yet.")
        except Exception as e:
            print(f"Error Cleaning Careem Data: {e}")

# Example Usage
if __name__ == "__main__":
    # Noon Data Cleaning
    noon = NoonCleaner("Noon_Sales_Data .csv")
    noon.clean()
    noon.save_data("Clean_Noon_Data.xlsx")

    # Amazon
    sheet_name = ["100 MPH", "100_Miles", "Wishcare"]
    amazon = AmazonCleaner("Amazon_Sales_Data.xlsx",sheet_name)
    amazon.clean()
    amazon.save_data("Clean_Amazon_Data.xlsx")

    # Revibe Data Cleaning
    revibe = RevibeCleaner("Revibe_Sales_Data.csv")
    revibe.clean()
    revibe.save_data("Clean_Revibe_Data.xlsx")



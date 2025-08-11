import pandas as pd
import numpy as np

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

# Noon cleaner
class NoonCleaner(BaseCleaner):
    def clean(self):
        try:
            self.read_data()
            self.data = self.data[['ordered_date','item_nr','sku','item_status','id_partner','country_code',
                                   'brand_en','family','product_subtype','marketplace','title_en',
                                   'is_fbn','base_price']]

            self.data = self.data.rename(columns={
                'ordered_date':'Date',
                'item_nr':'Order Number',
                'sku':'SKU',
                'item_status':'Status',
                'id_partner':'Partner Id',
                'country_code':'Country',
                'brand_en':'Brand Name',
                'family':'Category',
                'product_subtype':'Sub-Category',
                'marketplace':'Channel',
                'title_en':'Channel Item Name',
                'is_fbn':'Fullfilment',
                'base_price':'Sales Price'
            })


            self.convert_date('Date')

            # Add Month, Month Number, Year Column
            self.data.insert(1, 'Month', self.data['Date'].dt.strftime('%B'))
            self.data.insert(2, 'Month Number', self.data['Date'].dt.month)
            self.data.insert(3, 'Year', self.data['Date'].dt.year)

            # Add Nub Partner column
            self.data.insert(8, 'Nub Partner', self.data['Partner Id'].apply(self.get_nub_partner))

            # Add Partner SKU Column
            self.data.insert(15,'Partner SKU',self.data['Order Number'])

            # Units and GMV Column
            self.data.insert(18, 'Units', 1)
            self.data.insert(19, 'GMV', self.data['Sales Price'] * self.data['Units'])

            # Replace values
            self.data['Country'] = self.data['Country'].replace({'SA':'Saudi', 'AE':'UAE'})
            self.data['Channel'] = self.data['Channel'].replace({'noon':'Noon', 'noon rocket':'Noon', 'noon instant':'Noon'})
            self.data['Status'] = self.data['Status'].replace({'Shipped':'Delivered'})

            # Filter status
            self.data = self.data[~self.data['Status'].isin(['Unshipped', 'Pending','Undelivered','Confirmed','Created','Exported','Fulfilling'])]
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

            # Add Month, Month Number, Year
            self.data.insert(1, 'Month', self.data['Date'].dt.strftime('%B'))
            self.data.insert(2, 'Month Number', self.data['Date'].dt.month)
            self.data.insert(3, 'Year', self.data['Date'].dt.year)

            # Nub Partner and Brand
            self.data.insert(8, 'Nub Partner', self.data['Partner ID'].apply(self.get_nub_partner))
            self.data.insert(10, 'Brand Name', self.data['Channel Item Name'].apply(self.get_brand_name))
            self.data.insert(11, 'Category', self.data['Brand Name'].apply(self.get_category))
            self.data.insert(12, 'Sub-Category', self.data['Brand Name'].apply(self.get_sub_category))

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

            print(f"Cleaned Amazon Data Shape: {self.data.shape}")
        except Exception as e:
            print(f"Error Cleaning Amazon Data: {e}")

    # Brand, Partner, Category functions remain unchanged
    def get_brand_name(self, cin):
        l = str(cin).split()
        if ('CAT' or 'Caterpiller') in l:
            return 'CAT'
        elif 'Willow' in l:
            return 'The White Willow'
        elif 'Pink' in l:
            return 'The Pink Stuff'
        elif ('WishCare??' or 'Wishcare®' or 'WishCare') in l:
            return 'WishCare'
        elif ('O\'Neill' or "O\'NEILL") in l:
            return 'O\'NEILL'
        elif  ('Carry' or 'Potty') in l:
            return 'My Carry Potty'
        elif 'Superdry' in l:
            return 'Superdry'
        elif 'Botaniq' in l:
            return 'Botaniq'
        elif 'Everteen' in l:
            return 'Everteen'
        elif 'Hismile' in l:
            return 'Hismile'
        elif 'RADLEY' in l:
            return 'RADLEY'
        else:
            return 'Unknown'

    def get_nub_partner(self, pid):
        if pid == 'Wishcare':
            return 'Nub-Partner Wishcare'
        elif pid == '100 MPH':
            return 'Nub-Partner 100 MPH'
        elif pid == '100_Miles':
            return 'Nub-Partner 100_Miles'
        else:
            return 'Null'

    def get_category(self, bn):
        if bn in ['WishCare', 'The White Willow', 'The Pink Stuff','My Carry Potty']:
            return bn
        elif bn in ['CAT', "O\'NEILL", 'Superdry', 'Botaniq', 'RADLEY']:
            return 'Eyewear'
        else:
            return 'Null'

    def get_sub_category(self, bn):
        if bn in ['WishCare', 'The White Willow', 'The Pink Stuff','The Carry Potty']:
            return bn
        elif bn in ['CAT', "O\'NEILL", 'Superdry', 'Botaniq', 'RADLEY']:
            return 'Sunglasses'
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

            # ✅ Step 3: Convert Date Format and Strip Time
            self.convert_date('Date')
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





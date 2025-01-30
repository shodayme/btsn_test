import os
import pandas as pd
import pyodbc
from sqlalchemy import create_engine, text
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.logger_factory import LoggerFactory

server = 'localhost'  # SQL Server address
database = 'InvoicesDB'
username = 'sa'
password = 'Test_password1$'
driver = 'ODBC Driver 18 for SQL Server'  # ODBC driver


# Define connection string for pyodbc
CONN_STR = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"
DATA_PATH = "./input_data/"


class DataProcessor():
    """

    Data processor class. 
    Contains methods to read a csv input, apply transformations and save to a pre-defined mssqldb

    """

    def __init__(self, conn_str):
        self.conn_str = conn_str
        self.logger = LoggerFactory().get_logger(
            'ETL_logger', './logs/processor_logs.log')
        return

    def __read_csv_data(self, path):
        """
        Read CSV files from the specified  directory.
        """
        try:
            file = os.listdir(path)[0]
            with open(path + file, 'rb') as f:
                if file.endswith('.csv'):
                    csv_df = pd.read_csv(f, delimiter=',', dtype='unicode')
                    self.logger.info(
                        f'Successfully loaded the CSV files under {path}.')
        except Exception as e:
            print(e)
            self.logger.error(
                f'Could not load csv files {type(e).__name__} -- {str(e)}')
        return csv_df

    def __format_col_names(self, name):
        return name.replace(' ', '_').lower()

    def __format_date(self, input_date):
        return pd.to_datetime(input_date, errors='coerce')

    def _apply_transformations(self, df):
        try:
            df.dropna(inplace=True)
            df.columns = df.columns.map(self.__format_col_names)
            df.drop_duplicates(subset=[
                               'invoice', 'customer_id', 'country', 'invoicedate', 'stockcode'], inplace=True)
            df['invoicedate'] = self.__format_date(df['invoicedate'])
            # df['quantity'] = df['quantity'].apply(lambda x: abs(int(x))) # Assuming there is a typo in causing negative quantities in the csv file
            # Assuming there is a typo in causing negative quantities in the csv file
            df['quantity'] = df['quantity'].astype(int).abs()
            # df['price'] = df['price'].apply(lambda x: abs(float(x)))
            df['price'] = df['price'].astype(float).abs()
            df['stockcode'] = df['stockcode'].str.upper().str.strip()
            # df['stockcode'] = df['stockcode'].apply(lambda x: x.upper().strip()) #
            df['month'] = pd.to_datetime(df['invoicedate']).dt.month
            df = df.assign(total_price=lambda x: x['price'] * x['quantity'])
            self.logger.info('>> Transformations applied successfully ')
            return df
        except Exception as e:
            self.logger.error(
                f"Failed to apply transformations : {type(e).__name__} -- {str(e)}")

    def build_dimension(self, csv_df, key_col, df_columns):
        """
        Builds a dimension dataframe based on selected columns
        """
        dim_df = csv_df[df_columns].drop_duplicates(subset=[key_col])
        return dim_df

    def __build_dimensions(self, df, engine):
        """
        Buils ands inserts dimension tables data in the db
        """
        df_table_map = {'Customer_d': self.build_dimension(df, 'customer_id', ['customer_id']),
                        'Country_d': self.build_dimension(df, 'country', ['country']),
                        'Date_d': self.build_dimension(df, 'invoicedate', ['invoicedate', 'month']),
                        'Stock_d': self.build_dimension(df, 'stockcode', ['stockcode', 'description'])}
        for table_name, df in df_table_map.items():
            try:
                df.to_sql(table_name, engine, if_exists='append', index=False)
                self.logger.info(f" >>> Successfully inserted {df.shape[0]} rows in table {table_name}")
            except Exception as e:
                self.logger.error(
                    f">> Failed insert data in {table_name} : {type(e).__name__} -- {str(e)}")

    def __build_fact(self, df, engine):
        """
        Builds the fact table based on the original csv and the dimension tables
        """
        df.to_sql('invoices_raw', engine, if_exists='replace', index=False)
        
        with engine.connect() as conn:
            try:
                with conn.begin():
                    query = text("""
                                    INSERT into invoices_f(invoice, quantity, price, total_price, stockcode_key, invoicedate_key, customer_key, country_key)
                                    SELECT raw.invoice, raw.quantity, raw.price, raw.total_price, s.stockcode_key, d.invoicedate_key, c.customer_key, ctr.country_key
                                    FROM invoices_raw raw
                                    JOIN Stock_d s ON s.stockcode = raw.stockcode
                                    JOIN Date_d d ON d.invoicedate = raw.invoicedate
                                    JOIN Customer_d c ON c.customer_id = raw.customer_id
                                    JOIN Country_d ctr ON ctr.country = raw.country
                                    WHERE NOT EXISTS (
                                        SELECT 1 from invoices_f f
                                        WHERE  s.stockcode_key = f.stockcode_key
                                        AND d.invoicedate_key = f.invoicedate_key
                                        AND c.customer_key = f.customer_key
                                        AND ctr.country_key = f.country_key
                                        AND f.invoice = raw.invoice
                                 )
                                """)
                    conn.execution_options(autocommit=True).execute(query)
                    self.logger.info(">>> Fact table successfully populated")
            except Exception as e:
                self.logger.error(f">> Failed insert data in fact table: {type(e).__name__} -- {str(e)}", e)

    def analyze(self, df):
        print(df.describe())
        print("Null Values:\n", df.isnull().sum())

    def etl(self, path):
        """
        Execute the etl process
        """
        csv_df = self.__read_csv_data(path)
        transformed_df = self._apply_transformations(csv_df)
        engine = create_engine(self.conn_str)
        self.__build_dimensions(transformed_df, engine)
        self.__build_fact(transformed_df, engine)


def main():
    data_processor = DataProcessor(CONN_STR)
    data_processor.etl(DATA_PATH)


if __name__ == '__main__':
    main()

-- Create the database if it doesn't exist
IF NOT EXISTS (
    SELECT name 
    FROM sys.databases 
    WHERE name = 'InvoicesDB'
)
BEGIN
    CREATE DATABASE InvoicesDB;
    PRINT 'Database created successfully.';
END
ELSE
BEGIN
    PRINT 'Database already exists.';
END

GO
-- Wait for 5 seconds before proceeding
BEGIN
    PRINT 'Wait for 5 seconds before proceeding';
END
WAITFOR DELAY '00:00:5';

-- Switch to the database
USE InvoicesDB;
GO

CREATE TABLE [invoices_f] (
	[invoice_key] int IDENTITY(1,1) NOT NULL UNIQUE,
	[invoice] varchar(32) NOT NULL,
	[stockcode_key] int NOT NULL,
	[quantity] int NOT NULL,
	[price]	float	NOT	NULL,
	[invoicedate_key] int NOT NULL,
	[customer_key] int NOT NULL,
	[country_key] int NOT NULL,
	[total_price] float NOT NULL,
	PRIMARY KEY ([invoice_key]),
	CONSTRAINT uq_customer_country_stock_date UNIQUE ([invoice], [customer_key], [country_key],[invoicedate_key], [stockcode_key] ) -- Unique constraint

);

CREATE TABLE [Customer_d] (
	[customer_key] int IDENTITY(1,1) NOT NULL UNIQUE,
	[customer_id] nvarchar(32) NOT NULL UNIQUE,
	PRIMARY KEY ([customer_key])
);

CREATE TABLE [Country_d] (
	[country_key] int IDENTITY(1,1) NOT NULL UNIQUE,
	[country] nvarchar(32) NOT NULL UNIQUE,
	PRIMARY KEY ([country_key])
);

CREATE TABLE [Date_d] (
	[invoicedate_key] int IDENTITY(1,1) NOT NULL UNIQUE,
	[invoicedate] datetime NOT NULL UNIQUE,
	[month] int
	PRIMARY KEY ([invoicedate_key])
);

CREATE TABLE [Stock_d] (
	[stockcode_key] int IDENTITY(1,1) NOT NULL UNIQUE,
	[stockcode] varchar(32) NOT NULL UNIQUE,
	[description] nvarchar(64),
	PRIMARY KEY ([stockcode_key])
);

ALTER TABLE [invoices_f] ADD CONSTRAINT [invoices_f_fk2] FOREIGN KEY ([stockcode_key]) REFERENCES [Stock_d]([stockcode_key]);

ALTER TABLE [invoices_f] ADD CONSTRAINT [invoices_f_fk4] FOREIGN KEY ([invoicedate_key]) REFERENCES [Date_d]([invoicedate_key]);

ALTER TABLE [invoices_f] ADD CONSTRAINT [invoices_f_fk5] FOREIGN KEY ([customer_key]) REFERENCES [Customer_d]([customer_key]);

ALTER TABLE [invoices_f] ADD CONSTRAINT [invoices_f_fk6] FOREIGN KEY ([country_key]) REFERENCES [Country_d]([country_key]);


BEGIN
    PRINT 'Tables successfully created.';
END
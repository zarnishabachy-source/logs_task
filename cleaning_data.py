import pandas as pd
import numpy as np

#loading datasets
df1=pd.read_csv(r"C:\Users\User\Downloads\logs\input files\server-logs-table-Database_Query.csv")
df2=pd.read_csv(r"C:\Users\User\Downloads\logs\input files\server-logs-table-Error_Exception.csv")
df3=pd.read_csv(r"C:\Users\User\Downloads\logs\input files\server-logs-table-General.csv")
df4=pd.read_csv(r"C:\Users\User\Downloads\logs\input files\server-logs-table-Processing.csv")
df5=pd.read_csv(r"C:\Users\User\Downloads\logs\input files\server-logs-table-Render_Template.csv")
df6=pd.read_csv(r"C:\Users\User\Downloads\logs\input files\server-logs-table-Started_Request.csv")
df7=pd.read_csv(r"C:\Users\User\Downloads\logs\input files\server-logs-table-Completed_Request.csv")

print("data is loaded")
#reading shape of datasets
print(df1.shape)
print(df2.shape)
print(df3.shape)
print(df4.shape)
print(df5.shape)
print(df6.shape)
print(df7.shape)
#reading column names of each dataset
print(df1.columns)
print(df2.columns)
print(df3.columns)
print(df4.columns)
print(df5.columns)
print(df6.columns)
print(df7.columns)
#remove query data , rendered,line duaration(ms),line allocation columns froms server logs table  started request
df6 = df6.drop(
    ['Query Category', 'Rendered Template', 'Line Duration (ms)', 'Line Allocations'],
    axis=1
)
#save file to cleaned_files folder
df6.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Started_Request.csv",index=False)

#remove query category column from server logs table render template
df5 = df5.drop(['Query Category'], axis=1)
#save file to cleaned_files folder
df5.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Render_Template.csv",index=False)
#remove  query data , rendered,line duaration(ms),line allocation columns froms server logs table processing 
df4= df4.drop(['Query Category', 'Rendered Template', 'Line Duration (ms)', 'Line Allocations'],
    axis=1)
#save to cleaned_files folder
df4.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Processing.csv",index=False)

#remove query data , rendered,line duaration(ms),line allocation columns froms server logs table general
df3= df3.drop(['Query Category', 'Rendered Template', 'Line Duration (ms)', 'Line Allocations'],
    axis=1)
#save to cleaned_files folder
df3.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-General.csv",index=False)

#remove total views time(ms),query data , rendered,line duaration(ms),line allocation columns from server logs table error exception
df2= df2.drop(['Total Views Time (ms)','Query Category', 'Rendered Template', 'Line Duration (ms)', 'Line Allocations'],
    axis=1)
#save to cleaned_files folder
df2.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Database_Query.csv",index=False)

#remove rendered template and line allocation
df1= df1.drop(['Rendered Template', 'Line Allocations'], axis=1)
#save to cleaned_files folder
df1.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Error_Exception.csv",index=False)

#remove query category and render template 
df7= df7.drop(['Query Category', 'Rendered Template'], axis=1)
#save to cleaned_files folder   
df7.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Completed_Request.csv",index=False)
#replace null values with NULL in server logs table completed request
df7=df7.fillna('NULL')
#replace null values with NULL in server logs table general
df3=df3.fillna('NULL')
#save to cleaned_files folder
df3.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-General.csv",index=False)
#replace null values with NULL in server logs table processing
df4=df4.fillna('NULL')
#save to cleaned_files folder
df4.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Processing.csv",index=False)

#replace null values with NULL in server logs table started request
df6=df6.fillna('NULL')
#save to cleaned_files folder
df6.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Started_Request.csv",index=False)
#replace missing values with Null 

df1=df1.fillna('NULL')
#saved to cleaned files
df1.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Database_Query.csv",index=False)

#replace null values with NULL in server logs table error exception
df2=df2.fillna('NULL')
#save to cleaned_files folder
df2.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Database_Query.csv",index=False)

#replace null values with NULL in server logs table render template
df5=df5.fillna('NULL')
#save to cleaned_files folder
df5.to_csv(r"C:\Users\User\Downloads\logs\cleaned_files\server-logs-table-Render_Template.csv",index=False)
#missing values of each datasets
print(df1.isnull().sum())
print(df2.isnull().sum())
print(df3.isnull().sum())
print(df4.isnull().sum())
print(df5.isnull().sum())
print(df6.isnull().sum())
print(df7.isnull().sum())
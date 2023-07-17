

import numpy as np
import pandas as pd
import sqlite3 as sql
import dask.dataframe as dd
import pyarrow.csv as pv
import pyarrow.parquet as pq

# Create Csv file
fruits = ['Orange', 'Grape', 'Apple', 'Banana', 'Pineapple', 'Avocado']
colors = ['Red', 'Green', 'Yellow', 'Blue']

df = pd.DataFrame(columns=['fruit', 'price', 'color'])
df.index.name = 'id'

df['fruit'] = np.random.choice(fruits, 1000000)
df['price'] = np.random.randint(10, 101, 1000000)
df['color'] = np.random.choice(colors, 1000000)
df.index += 1
df.to_csv('mydata.csv')


# Task 1 - CSV and SQL

# Section 1
# creating a DB if not exist and creating a connection to it.
conn = sql.connect('mydb.db')
c = conn.cursor()
# Executing statement to create a table based on the CSV schema
c.execute('''CREATE TABLE IF NOT EXISTS mydata (id INTEGER , fruit TEXT, price INTEGER , color TEXT)''')
df = pd.read_csv('mydata.csv')

# Section 2
# Loading the into the table
df.to_sql('mydata', conn, if_exists='append', index = False)
c.execute('''SELECT * FROM mydata d WHERE d.fruit = 'Banana' AND d.price = 40 AND d.color = 'Blue' ''')

# Section 3
# in this SQL statment the projection part is " SELECT * FROM mydata d "
# and the predicate is "WHERE d.fruit = 'Banana' AND d.price = 40 AND d.color = 'Blue'"

c.execute('''SELECT d.fruit, count(*) FROM mydata d WHERE d.price >50 GROUP BY d.fruit ''')
# in this SQL statment the projection part is " SELECT d.fruit, count(*) FROM mydata d"
# and the predicate is "WHERE d.price >50 GROUP BY d.fruit"
conn.commit()
conn.close()

# Task 2 - CSV and Parquet

# Section 1
# A function to count the number of lines in a CSV file
def count_rows(csv_file):
    with open(csv_file, 'rb') as f:
        return f.read().decode(encoding='utf-8').count('\n')

# Section 2
# creating PyArrow Parquet file
table = pv.read_csv('mydata.csv')
pq.write_table(table, 'mydatapyarrow.parquet')

# Section 3
# creating Dask Parquet file
df = dd.read_csv('mydata.csv')
df.to_parquet('mydatadask.parquet', write_index=False)

# Section 4
# creating Pandas Parquet file
df = pd.read_csv('mydata.csv')
df.to_parquet('mydatapandas.parquet', index=False)

# Section 5
# A Dask DataFrame is a large parallel DataFrame composed of many smaller Pandas DataFrames, split along the index.
# Dask is designed, among other things, to enable parallel computations. when Dask reads a directory into a dataframe
# it can read multiple files, one file per partition. When a Parquet file is created in Dask in creates directory of
# the file + _metadata files + _common_metadata, which is different then how Pandas and PyArrow create a file. Those
# files include information about the schema of the full dataset (_common_metadata) and potentially all row group
# metadata of all files in the partitioned dataset as well (_metadata). the schema of the dataset can be read from a
# _common_metadata file or from any one of the data files Using those files can give a more efficient creation of a
# parquet Dataset, since it can use the stored schema and and file paths of all row groups, instead of inferring the
# schema and crawling the directories for all Parquet files. that is the reason why when file is created using Dask
# it's created as a partition, to enable this kind of functionality.

# Task 3 - split CSV files

# Section 1
# A function to calculates the size of a CSV file in bytes
def get_csv_size(csv_file):
    with open(csv_file, 'rb') as f:
        return len(f.read())

# Section 2
# A function that returns the number of lines in the first half of the CSV
# if counts the number of '\n', if the split causes the last line to split, one row is added to the total count.
def first_chunk(csv_file, middle):
    with open(csv_file, 'rb') as f:
        d1 = f.read(middle).decode(encoding='utf-8')
        if d1[-1] != '\n':
            number_of_lines = d1.count('\n') + 1
        else:
            number_of_lines = d1.count('\n')
        return number_of_lines

# A function that returns the number of lines in the second half of the CSV
def last_chunk(csv_file, middle):
    with open(csv_file, 'rb') as f:
        f.seek(middle + 1, 0)
        d2 = f.read(middle).decode(encoding='utf-8')
        return d2.count('\n')

csv_file = 'mydata.csv'
file_byte_size = get_csv_size(csv_file)
middle = file_byte_size // 2
first_chunk_lines_count = first_chunk(csv_file, middle)
last_chunk_lines_count = last_chunk(csv_file, middle)

print('========== Task 3  ==========')
print('Total number of lines in CSV file:{}\n'.format(count_rows(csv_file)))
print('========= Section 2 =========')
print('Number of lines in first chunk:{}'.format(first_chunk_lines_count))
print('Number of lines in last chunk:{}'.format(last_chunk_lines_count))
print('Total number of lines in both chunks:{}\n'.format(first_chunk_lines_count + last_chunk_lines_count))

# Section 3
# Because we split the file in the middle, one line may be split in half
# and it is counted twice, once in each chunk, resulting in one extra line count in the summation of both chucks.

# Section 4
# We'll read until the middle byte plus a few bytes to the end of the line we split,
# maintaining data integrity and solving the wrong line count.
def first_chunk_plus(csv_file, middle, end):
    with open(csv_file, 'rb') as f:
        d1 = f.read(middle).decode(encoding='utf-8')
        updated_middle = middle
        for _ in range(end - middle):
            if d1[-1] != '\n':
                d1 += f.read(1).decode(encoding='utf-8')
                updated_middle += 1
            else:
                number_of_lines = d1.count('\n')
                break
        return number_of_lines, updated_middle

first_chunk_lines_count_updated, updated_middle = first_chunk_plus(csv_file, middle, file_byte_size)
last_chunk_lines_count_updated = last_chunk(csv_file, updated_middle)
print('========= Section 4 =========')
print('Number of lines in first chunk:{}'.format(first_chunk_lines_count_updated))
print('Number of lines in last chunk:{}'.format(last_chunk_lines_count_updated))
print('Total number of lines in both chunks:{}\n'.format(first_chunk_lines_count_updated + last_chunk_lines_count_updated))

# Section 5
# In this function we read each chunk based on the chunk_size that was given as an input.
# if the chunk read results in a line split, we continue to read until we read the entire line.
# Thus every chunk will have complete lines and will be around the chunk_size that was given as an input.
def count_chunks(csv_file, chunk_size, file_size):
    f = open(csv_file, 'rb')
    chunk_number = 0
    total_number_of_lines = 0
    while True:
        chunk_number += 1
        d = f.read(chunk_size).decode(encoding='utf-8')
        if not d: break

        for i in range(file_size - chunk_number * chunk_size):
            if d[-1] != '\n':
                d += f.read(1).decode(encoding='utf-8')
            else: break
        number_of_lines_in_chunk = d.count('\n')

        print('Number of lines in chunk{}: {}'.format(chunk_number, number_of_lines_in_chunk))
        total_number_of_lines += number_of_lines_in_chunk
    print('Total number of lines: {}'.format(total_number_of_lines))

print('========= Section 5 =========')
count_chunks('mydata.csv', 1024 * 1024 * 16, file_byte_size)

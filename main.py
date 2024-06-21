import os
import csv
import psycopg2

# Configurations
src_dbname = ""
src_username = ""
src_password = ""
src_host = ""
src_port = 5432
src_schema = ""
src_table = ""

tgt_dbname = ""
tgt_username = ""
tgt_password = ""
tgt_host = ""
tgt_port = 5432
tgt_schema = ""
tgt_table = ""

csv_path = r"temp_db_data.csv"

# Operations
query = f"""
    SELECT * 
    FROM {src_schema}.{src_table}
    WHERE    
    """
copy_query = "COPY({0}) TO STDOUT WITH CSV HEADER".format(query)

# sort_query = f"SELECT * FROM {tgt_schema}.{tgt_table} ORDER BY date DESC, time DESC"

# delete_query = f"DELETE FROM {tgt_schema}.{tgt_table} WHERE date < current - 14"

tgt_conn = psycopg2.connect(
    dbname=tgt_dbname,
    user=tgt_username,
    password=tgt_password,
    host=tgt_host,
    port=5432,
)

src_conn = psycopg2.connect(
    dbname=src_dbname,
    user=src_username,
    password=src_password,
    host=src_host,
    port=src_port,
)

src_cur = src_conn.cursor()
tgt_cur = tgt_conn.cursor()

# Create target table if not exists
src_cur.execute(
    f"SELECT * FROM information_schema.columns WHERE table_name = '{src_table}' ORDER BY ordinal_position"
)

src_table_structure = src_cur.fetchall()

column_defs = []
for column in src_table_structure:
    column_name = column[3]
    data_type = column[7]
    column_defs.append(f"{column_name} {data_type}")

create_table_query = (
    f"CREATE TABLE IF NOT EXISTS {tgt_schema}.{tgt_table} ({', '.join(column_defs)});"
)

tgt_cur.execute(create_table_query)
tgt_conn.commit()

# Export data from source table into csv
with open(csv_path, "w", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)

    src_cur.copy_expert(copy_query, csv_file)

print("\nData is exported.")

# Import data from csv to target table
with open(csv_path, "r", encoding="utf-8") as csv_file:
    tgt_cur.copy_expert(
        f"COPY {tgt_schema}.{tgt_table} FROM STDIN WITH CSV HEADER DELIMITER ','",
        csv_file,
    )

# tgt_cur.execute(sort_query)
# tgt_cur.execute(delete_query)

print("Data is transfered.")

tgt_conn.commit()

src_cur.close()
tgt_cur.close()
src_conn.close()
tgt_conn.close()

os.remove(csv_path)

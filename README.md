# Project-4-Data-Warehouse

## Introduction

The music streaming startup Sparkify has expanded its user base and song database and is now looking
to transition its operations and data to the cloud. The data is currently stored in S3, comprising a 
directory of JSON logs capturing user activity on the app and another directory containing JSON meta
data on the songs within the app.

## Summary

This project has integrated song listen log files with song metadata to streamline analytics. Using 
the Python SDK, a Redshift cluster was established, and a data pipeline, developed in Python and SQL,
crafted a data schema tailored for analytics. JSON data was transferred from an S3 bucket to Redshift
staging tables, then inserted into a star schema featuring fact and dimension tables. Analytics 
queries on the `songplays` fact table are simple, and additional fields are easily accessible in the 
four dimension tables: `users`, `songs`, `artists`, and `time`. The chosen star schema is ideal for 
this application, offering ease of denormalization, simplicity in queries, and efficient aggregations.

## Installation

```bash
$ pip install -r requirements.txt
```

## Required Files

**`dwh.cfg`** - specifications for configuring the Redshift cluster and setting up data import.

**`create_cluster.py`** - establish an IAM role, set up a Redshift cluster, and enable TCP connections. Pass `--delete` flag to initiate resource deletion.

**`create_tables.py`** - recreate and drop tables.

**`etl.py`** - transfer data to staging tables and populate fact and dimension tables within the star schema.

**`sql_queries.py`**:

- Establishing and removing staging and star schema tables.
- Tansferring JSON data from S3 to Redshift staging tables.
- Moving data from staging tables to fact and dimension tables within the star schema.

## Instructions for executing scripts

- Set variables in `dhw.cfg` file:
<br />  **[AWS]**
<br />  KEY: AWS_ACCESS_KEY_ID
<br />  SECRET: AWS_SECRET_ACCESS_KEY
<br /> **[CLUSTER]**
<br /> DB_PASSWORD

- Establish an IAM role, set up a Redshift cluster, and arrange TCP connectivity.

```bash
$ python create_cluster.py
```

- Finish filling in `dwh.cfg` with the outputs obtained from `create_cluster.py`.
<br /> **[CLUSTER]**
<br /> HOST
<br /> **[IAM_ROLE]**
<br /> ARN

- Drop and recreate tables:

```bash
$ python create_tables.py
```

- Run the ETL pipeline:

```bash
$ python etl.py
```

- Delete an IAM role and a Redshift cluster:
```bash
$ python create_cluster.py --delete
```

## Future Tasks

- Implement data quality checks.
- Develop a dashboard for analytical queries on the new database.

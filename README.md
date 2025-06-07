# Assessment
## Introduction
The purpose of this document is to explain the assumptions made and some the technical decisions taken.

## Architecture
This assessment used hexagonal architecture to keep business logic isolated
taking the advantages of this architecture such as modular, business logic easy to test and 
adaptable to changes. This kind of architecture makes scalability easy.

Vertical slicing was not applied for the assessment.

## Application
### Introduction
This section explains all decisions related to
the application and the assumptions taken.

### General assumptions
#### Secrets
All secrets are hardcoded. Obviously this is really bad practice. 
Secrets must be injected using cloud secrets manager like 
Azure KeyVault or AWS Secrets Manager.
On premise a KMS such as Hashicorp Vault must be used.

#### Configuration linked to environments
Configurations such as database hosts, ports, etc could be provided
using .env files or environment variables.

#### Dependency injection
Library kink was used to achieve dependency injection in this assessment. 
Objects to be injected could be linked with environments or other situations. 
Sometimes to perform unit testing mock objects must be injected.

No bootstraps scripts were created for the assessment but for real application
are advised.


### Data Ingestion Pipeline
The choice of Pandas is driven by the many advantages it offers. 

ETL load from file and then go through a service to have all the validations
or any application logic to be applied to each entry.

Issue in a row or failed validation for one entity 
should not block other rows/entities. For that reason
there are mechanism defined to store not parsed rows in batch. Insert in services
will return a list of entities rejected due outliers, inconsistencies, etc.


#### Topic not covered
"Design the pipeline to be resilient and scalable, capable of processing imperfect real-world data"

The above sentence is quite open, in this imperfect real-world data 
the different situations are close to infinity. In my experience, each project
handle a set of common imperfections that may differ between other projects.
Just an example if some metrics are provided sometime only the value 
and sometimes value + units, this kind of imperfections could be sanityze in
a preprocess step.

### Data Processing & Analytics
Two files were created for this topic, the batch that contains the logic and 
entry point script. 

The result were stored in a table with the patient_id 
plus all metrics (mix, max and mean). To find a row will be quite fast thanks
to the index created for patient_id column. 


Optimization was not put in place due the volume of data is not enough.
Ideas for optimization:
* Use PostgreSQL partitions to speed up data loading. 
* Introduce a column acting as a flag, if a client don't provide metrics 
between two executions there is no reason to recalc them.
* Split patients by a category such as state, country or even age group.
Adding this column the batch could be executed in parallel for all clients
and taking the advantages of PostgreSQL partitions during loading data.

## Database (PostgreSQL)
### Introduction
This section is to explain all the decision related to database engine and
solution designed.

In folder ddl of this repository you could find ddl files 
for the three tables created

### Why choose Psycopg2 over SQLAlchemy?
Psycopg2 is better suited to data engineering tasks. Its performance and flexibility
is better for handling complex SQL scenarios.

SQLAlchemy is great tool but not for performance tasks. ORM's like SQLAlchemy 
are better suited for web applications. 

Both tools can be used in the same project, especially since a hexagonal 
architecture has been selected, allowing the same repository to be 
implemented in different ways.

### Patients table
Patients table has an auto increment sequence for column "patient_id". 
Hash index for column email was created assuming the patient could be search
by email and hash index has a good performance if you only need to perform
equals comparisons.
Btree index for column patient_id was created because this index will be use 
for equality operation as well as greater or lower comparisons.

### Biometrics table
The biometrics table contains a foreign key (patient_id) 
that links to the patients table.
An index was created with columns biometrics_id and test_date. 
This index is really important for pagination performance.
Two columns where selected for the index to prevent inconsistencies if 
data is modified between requests. 

### Biometrics_analytics table
The biometrics_analytics table contains a foreign key (patient_id) 
that links to the patients table.
Betree index for column patient_id was created because this index will be use 
for equality operation as well as greater or lower comparisons can be added
if a future.

### Assumptions
For the assessment no partitions were defined in tables. 
PostgreSQL partition mechanism is a really powerful way to 
improve performance. For example if patients table has country column, 
when a patient from Canada is searched, patients from other countries 
will not be even loaded. This will improve performance and reduce costs.

## API Implementation
### Introduction
This section is to explain all the decision related to API 

### Pagination strategy
For pagination a next_token_page was created. 
For patient resource next_token_page is patient_id but for
biometrics history next_token_page is composed by biometric_id and
test_date. The token is converted from a tuple to json and 
encoded in base64, in the next call then the token is decoded,
obtaining the tuple again. (This was made only for demonstration)

### Upsert biometrics
For upsert, MERGE was performed in database instead 
of check if exists and if yes update and if not insert.

### Biometrics analytics
A table was created storing metrics (mean, max, min) using the patient_id
as primary key and foreign key. 

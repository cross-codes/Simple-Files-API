<div align="center">
<h1>📁 Simple File API</h1>

A very simple API for hosting and serving files on a containerised SQL database

Model solution for the Coding Club Summer recruitment task
</div>

---

This API uses a containerized PostgreSQL database to store binary files.
It supports extremely simple CRUD operations, and currently works with `curl`,
by specifying the file via an absolute path on a local file-system.

**This task is a proof-of-concept for being able to access a containerised database via a
TCP socket.**

## Set up process

First, pull the official docker image for PostgreSQL:

```bash
docker pull postgres:latest
```

Then, once the `docker` daemon is running on some socket, `RUN` the container using:

```bash
docker run --name <CONTAINER_NAME> -e POSTGRES_PASSWORD=<PASSWORD> -d postgres:latest
```

The console can be accessed using the following command:

```bash
docker exec -it <CONTAINER_NAME> bash
```

`STDIN` persists with the `-i` flag, and a `psuedo-TTY` is created from which
the `psql` interface can be accessed:

```bash
psql -U postgres
```

## Creating the database

To create the database, we define the command in an `init.sql` file so this
process is automated. The contents of the file are as such:

```sql
-- init.sql
CREATE TABLE files (
  id                serial PRIMARY KEY,
  file_name         varchar(80),
  file_content      BYTEA NOT NULL,
  created_at        DATE NOT NULL
)
```

Copy this file into the container:

```bash
docker cp init.sql <CONTAINER_ID>:/init.sql
```

and then use `psql` to execute the commands contained
within its contents:

```bash
# Within the container, create a database called files_api first
psql -U postgres -d files_api -a -f init.sql
```

This will, according to the contents of `init.sql`, create a table called files with
the specified relations.

## The connection

We will connect to this database without a `.yml` compose file.

First stop the container

```bash
docker stop <CONTAINER_NAME>
```

Create a new network specifically for PostgreSQL:

```bash
docker network create --subnet=172.18.0.0/16 <NETWORK_NAME>
```

Connect this container with the custom network:

```bash
docker network connect --ip 172.18.0.22 <NETWORK_NAME> <CONTAINER_NAME>
```

You can then start the container:

```bash
docker start <CONTAINER_NAME>
```

Note the IP that this container will now always be hosted on:

```bash
docker inspect --format \
     '{{.NetworkSettings.Networks.<NETWORK_NAME>.IPAddress}}' <CONTAINER_NAME>
```

**Failure to execute the above steps could result in an inconsistent host address
every time the container is restarted, because docker compose is not being used.**

---

Create a `.env` file with the following contents:

```env
DB_NAME=<DB_NAME>
DB_USER="postgres"
DB_PASS=<DB_PWD>
DB_HOST=<RESULT_OF_THE_PREVIOUS_COMMAND>
DB_PORT="5432"
```

## The API

The `main.py` file contains all the business logic for connecting to the API, and
performing creation, retrieval and deletion operations. The updation operation
can be performed, but is out of scope for this task in particular.

A full fledged, scalable implementation is expected to be made in the future.

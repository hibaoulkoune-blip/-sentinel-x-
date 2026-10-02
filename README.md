# SENTINEL-X



## Intelligent Infrastructure Monitoring & Incident Management Platform



SENTINEL-X is a web-based infrastructure monitoring and incident management platform built with a FastAPI backend, PostgreSQL database, and React frontend.



The platform monitors HTTP services, records health checks, detects response-time anomalies, manages incidents, and provides a web dashboard for monitoring system activity.



## Current Status



The project is under active development.



Implemented components include:



* HTTP monitor management

* HTTP health checks

* Check history

* PostgreSQL persistence

* Alembic database migrations

* Automated monitoring scheduler

* Incident management

* Response-time anomaly detection

* REST API with FastAPI

* Automated tests with pytest

* Test coverage measurement

* GitHub Actions continuous integration

* React/Vite frontend foundation



Some components are still under development, including advanced recovery workflows, authentication and RBAC, production hardening, and additional dashboard capabilities.



## Main Features



### Monitoring



* Create, update, list, and delete HTTP monitors

* Enable or disable monitors

* Configure monitoring intervals and request timeouts

* Execute HTTP checks

* Record service status, HTTP status codes, response time, and errors



### Incident Management



* Detect repeated monitoring failures

* Create incidents from monitoring failures

* Track incident status

* Resolve open incidents after service recovery



### Anomaly Detection



* Analyze response-time behavior

* Calculate statistical indicators such as mean, standard deviation, and Z-score

* Assign anomaly severity levels



### Scheduler



The monitoring scheduler periodically processes enabled monitors and stores their check results.



### REST API



The backend exposes REST endpoints through FastAPI and provides interactive documentation through Swagger UI.



### Testing and Quality



The backend uses pytest and pytest-asyncio for automated testing, with coverage measurement through pytest-cov.



### Continuous Integration



GitHub Actions is configured to automatically run the backend test suite in a PostgreSQL-based CI environment.



### Frontend



A React/Vite frontend is being developed to provide a centralized dashboard for monitors, incidents, anomalies, and system information.



## Technology Stack



| Component  | Technology                         |

| ---------- | ---------------------------------- |

| Backend    | Python 3.11, FastAPI               |

| Frontend   | React, Vite                        |

| Database   | PostgreSQL                         |

| ORM        | SQLAlchemy 2.x                     |

| Migrations | Alembic                            |

| Testing    | pytest, pytest-asyncio, pytest-cov |

| API Client | HTTPX                              |

| Containers | Docker, Docker Compose             |

| CI         | GitHub Actions                     |



## Project Structure



```text

sentinel-x/

â”œâ”€â”€ backend/

â”‚   â”œâ”€â”€ app/

â”‚   â”‚   â”œâ”€â”€ api/

â”‚   â”‚   â”œâ”€â”€ monitors/

â”‚   â”‚   â”œâ”€â”€ checks/

â”‚   â”‚   â”œâ”€â”€ incidents/

â”‚   â”‚   â”œâ”€â”€ anomaly/

â”‚   â”‚   â”œâ”€â”€ scheduler/

â”‚   â”‚   â””â”€â”€ database/

â”‚   â”œâ”€â”€ tests/

â”‚   â”œâ”€â”€ alembic/

â”‚   â”œâ”€â”€ Dockerfile

â”‚   â””â”€â”€ docker-compose.yml

â”œâ”€â”€ frontend/

â”œâ”€â”€ .github/

â”‚   â””â”€â”€ workflows/

â”œâ”€â”€ backend/openapi.json

â””â”€â”€ README.md

```



## Getting Started



### Backend



From the project root:



```bash

cd backend

```



Create and activate the virtual environment:



```bash

python -m venv .venv

```



On Windows:



```bash

.venv\\Scripts\\activate

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Start the API:



```bash

uvicorn app.main:app --reload

```



Backend:



```text

http://127.0.0.1:8000

```



Interactive API documentation:



```text

http://127.0.0.1:8000/docs

```



Health endpoint:



```text

http://127.0.0.1:8000/api/v1/health

```



### Frontend



From the project root:



```bash

cd frontend

npm install

npm run dev

```



The Vite development server is normally available at:



```text

http://localhost:5173

```



## Running Tests



From the backend directory:



```bash

pytest -q

```



For coverage:



```bash

pytest --cov=app --cov-report=term-missing -q

```



## Database



The project uses PostgreSQL with SQLAlchemy and Alembic.



To apply database migrations:



```bash

alembic upgrade head

```



## Docker



The backend Docker Compose configuration is located in:



```text

backend/docker-compose.yml

```



From the project root:



```bash

cd backend

docker compose up --build -d

```



Check running containers:



```bash

docker compose ps

```



## Monitoring Workflow



1. Create an HTTP monitor.

2. Configure its interval and timeout.

3. The scheduler executes monitoring checks.

4. Each check stores the service status and response information.

5. Repeated failures can generate an incident.

6. Response-time analysis can detect anomalies.

7. Service recovery can resolve an open incident.

8. The frontend provides a centralized view of monitoring data.



## API Documentation



FastAPI provides interactive API documentation at:



```text

http://127.0.0.1:8000/docs

```



The generated OpenAPI specification is maintained in:



```text

backend/openapi.json

```



## Project Objective



The objective of SENTINEL-X is to build a practical infrastructure monitoring platform while applying software engineering principles in:



* Backend development

* REST API design

* Database architecture

* Automated monitoring

* Anomaly detection

* Incident management

* Automated testing

* Continuous integration

* Containerization

* Frontend development



## Author



**Hiba Oulkoune**



GÃ©nie Informatique

Ã‰cole SupÃ©rieure de Technologie de BÃ©ni Mellal





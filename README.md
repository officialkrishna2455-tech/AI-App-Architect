# Requirement Compiler

A production-grade compiler that transforms natural language software requirements into executable application blueprints.

## Architecture

```
Requirements → Lexer → Parser → AST → Semantic Analyzer → Architecture Planner
→ Schema Generator → Consistency Engine → Validation Engine → Repair Engine
→ Runtime Simulator → Final Executable Specification
```

### Compiler Pipeline (9 Stages)

| Stage | Module | Input | Output |
|-------|--------|-------|--------|
| 1. Lexer | `requirement_lexer` | Raw text | `list[Token]` |
| 2. Parser | `requirement_parser` | Tokens | `RequirementAST` |
| 3. Semantic Analyzer | `semantic_analyzer` | AST | Enriched AST |
| 4. Architecture Planner | `architecture_planner` | AST | `ArchitecturePlan` |
| 5. Schema Generator | `schema_generator` | AST + Plan | 5 Schemas |
| 6. Consistency Engine | `consistency_engine` | Schemas | Knowledge Graph + Issues |
| 7. Validation Engine | `validation_engine` | Schemas | `ValidationReport` |
| 8. Repair Engine | `repair_engine` | Schemas + Issues | Repaired Schemas |
| 9. Runtime Simulator | `runtime_simulator` | Schemas | `SimulationReport` |

### Generated Schemas

1. **UI Schema** — Pages, components, navigation, theme
2. **API Schema** — Endpoints, middleware, error codes
3. **DB Schema** — Tables, columns, relations, migrations
4. **Auth Schema** — Roles, permissions, policies, JWT config
5. **Business Logic Schema** — Workflows, rules, events, integrations

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd "FULLY BUILT COMPILER"

# Install all dependencies
make install

# Or manually:
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### Development

```bash
# Start both backend and frontend
make dev

# Or separately:
make dev-backend   # http://localhost:8000
make dev-frontend  # http://localhost:3000
```

### Testing

```bash
# Run all tests
make test

# Run pipeline integration test
make test-pipeline

# Run evaluation framework (20 prompts)
make evaluate
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/compile` | Compile requirements into schemas |
| `POST` | `/api/validate` | Re-validate an existing run |
| `POST` | `/api/repair` | Repair validation issues |
| `POST` | `/api/simulate` | Run simulation on schemas |
| `GET` | `/api/runs` | List compilation runs |
| `GET` | `/api/runs/{id}` | Get run details |
| `GET` | `/api/metrics` | Get aggregate metrics |
| `POST` | `/api/auth/login` | Authenticate |
| `POST` | `/api/evaluate` | Run evaluation framework |

## Example

```bash
curl -X POST http://localhost:8000/api/compile?sync=true \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a CRM with login, contacts, dashboard, role-based access, premium plans, payments, and analytics."
  }'
```

## Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Cloud Deployment

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables from `.env.example`

### Frontend (Vercel)
1. Import your repository on Vercel
2. Set framework preset to Next.js
3. Set `NEXT_PUBLIC_API_URL` to your Render backend URL
4. Deploy

## Evaluation Framework

20 test prompts (10 production + 10 adversarial) with tracked metrics:

- **Success Rate**: % of prompts producing valid output
- **Repair Rate**: Average repairs per run
- **Latency**: P50/P95/P99 per stage
- **Simulation Pass Rate**: % of simulated scenarios passing
- **Validation Pass Rate**: % of validation rules passing

## Tech Stack

- **Backend**: FastAPI + Python 3.11 + Pydantic v2 + SQLAlchemy + spaCy
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Framer Motion
- **Database**: SQLite
- **Deployment**: Docker + Vercel + Render

## License

MIT

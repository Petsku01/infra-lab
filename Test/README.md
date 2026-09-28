
## Quick Start

```bash


# Asenna vaatimukset (npm)
npm install

# Aloita testi servu 
npm run dev




# Databasen teko
npm run db:setup

# tai manuaalisesti:
# npx prisma migrate dev
# npx prisma generate


```

Avaa [http://localhost:5173](http://localhost:3000) 



## Projektin sunniteltu rakenne

```
├── src/
│   ├── frontend
│   │
│   └── backend/             # Backend (Express + Node.js)
│       ├── routes/          # API reitit
│       ├── services/        # Logiiigat
│       ├── middleware/      # turvallisuus (I have one idea)
│       ├── utils/           # Serverin perustarpeet
│       └── config/          # Configuraatio tiedostot
│
├── prisma/                  # Database (Prisma ORM)
│   ├── schema.prisma        # Database scheema
│   ├── migrations/          # Database migraatiot?
│   └── seed.js              # Database seedi
│
├── docs/                    # Documentation
├── public/                  # Static assets
└── scripts/                 # Build & deployment scripts
```



### Kehitys

```bash
npm run dev          # Aloita molemmat frontend and backend
npm run frontend     # Aloita vain frontend 
npm run backend      # Vain backend 
npm run preview      # Esikatsele, ei toiminnassa
```

### Database

```bash
npm run db:setup     # Aloita database (migrate + generate)
npm run db:migrate   # Yhdistä database 
npm run db:generate  # Genroi Prisma client
npm run db:studio    # Avaa Prisma Studio
npm run db:reset     # Resetttaa database //ei saa tehdä ilman lupaa
npm run db:seed      # Databaseen testi dataa
```

### Koodin korjaus

```bash
npm run lint         # Check code quality
npm run lint:fix     # Fix linting issues
npm run format       # Format code with Prettier
npm run format:check # Check code formatting
```

### Tuotantoon

```bash
npm run build        # Rakenna tuotantoon
npm start            # Aloita tuotantoservu
```

## Template ominaisuudet

### Frontend


### Backend









### Kontaktin hallinnointi
```bash
GET    /contact/list     # Get all contacts
GET    /contact/:id      # Get specific contact  
POST   /contact          # Create new contact
PUT    /contact/:id      # Update contact
DELETE /contact/:id      # Delete contact
```

### Task Management  
```bash
GET    /task/list        # Get all tasks
GET    /task/:id         # Get specific task
POST   /task             # Create new task
PUT    /task/:id         # Update task
DELETE /task/:id         # Delete task
```

### Project Management
```bash
GET    /project/list     # Get all projects
GET    /project/:id      # Get specific project
POST   /project          # Create new project
PUT    /project/:id      # Update project
DELETE /project/:id      # Delete project
```

### Health Check
```bash
GET    /health           # Server status check
```

All endpoints return standardized JSON responses:
```javascript
{
  "success": boolean,    // Operation status
  "data": any,          // Response payload  
  "message": string,    // Human-readable message
  "timestamp": string   // ISO timestamp
}
```





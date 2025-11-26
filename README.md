# Space Cargo Stowage 🚀📦

**ISRO Hackathon Project**

This project aims to optimize the placement of items in various containers and streamline the handling of waste on the International Space Station (ISS). It utilizes a full-stack approach to manage inventory, process cargo data via CSVs, and visualize stowage configurations.

## 🌟 Features

- **Cargo Optimization**: Algorithms to determine the most efficient placement of items in storage containers.
- **Waste Management**: Tracking and handling protocols for ISS waste disposal.
- **Data Import**: Support for uploading cargo manifests via CSV (using `multer` and `csv-parser`).
- **Interactive UI**: React-based interface for visualizing stowage and managing inventory.
- **Robust Backend**: REST API built with Express and PostgreSQL for reliable data persistence.

## 🛠️ Tech Stack

### Frontend (`/space-cargo-stowage`)
- **Framework**: React (Vite)
- **HTTP Client**: Axios
- **Styling/UI**: CSS, React Icons
- **Performance**: React Window (for handling large lists)

### Backend (`/space-cargo-stowage-backend`)
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: PostgreSQL (`pg`)
- **File Handling**: Multer (uploads), CSV Parser
- **Environment**: Dotenv

## 📋 Prerequisites

Before running the project, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v16 or higher recommended)
- [PostgreSQL](https://www.postgresql.org/)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/PigeonOfPrison/space-cargo-stowage-project.git
cd space-cargo-stowage-project
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:

```bash
cd space-cargo-stowage-backend
npm install
```

**Configuration:**
Create a `.env` file in the `space-cargo-stowage-backend` directory with your database credentials:
```env
PORT=5000
DB_USER=your_postgres_user
DB_HOST=localhost
DB_NAME=your_database_name
DB_PASSWORD=your_postgres_password
DB_PORT=5432
```

Start the backend server:
```bash
npm start
# Or for development with auto-reload:
npm run dev
```

### 3. Frontend Setup
Open a new terminal, navigate to the frontend directory, and install dependencies:

```bash
cd space-cargo-stowage
npm install
```

Start the frontend development server:
```bash
npm run dev
```
The application should now be running (usually at `http://localhost:5173`).

## 📂 Project Structure

- **`space-cargo-stowage/`**: The React frontend application.
- **`space-cargo-stowage-backend/`**: The Node.js/Express API server.
- **`test files/`**: Sample CSVs and data files for testing cargo algorithms.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

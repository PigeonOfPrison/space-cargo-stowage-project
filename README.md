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

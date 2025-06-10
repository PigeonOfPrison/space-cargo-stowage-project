import 'dotenv/config'; // Load environment variables from .env file
import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
    user : process.env.DB_USER,
    host : process.env.DB_HOST,
    database : process.env.DB_NAME,
    password : process.env.DB_PASSWORD,
    port : process.env.DB_PORT || 5432
});

const initDatabase = async () => {
    //Create a temporary pool to connect to postgres database for database creation
    const tempPool = new Pool({
        user: process.env.DB_USER || 'postgres',
        host: process.env.DB_HOST || 'localhost',
        database: process.env.DB_NAME || 'postgres', // Connect to default postgres database
        password: process.env.DB_PASSWORD,
        port: process.env.DB_PORT || 5432,
    });


    try {
        // Create database if it doesn't exist
        await tempPool.query(`
            CREATE DATABASE space_cargo_db
            WITH 
            OWNER = postgres
            ENCODING = 'UTF8'
            TABLESPACE = pg_default
            CONNECTION LIMIT = -1
        `);
        console.log('Database created successfully');
    } catch (error) {
        if (error.code !== '42P04') { // Error code for "database already exists"
            console.error('Error creating database:', error);
        } else {
            console.log('Database already exists');
        }
    } finally {
        await tempPool.end(); // Close the temporary pool
    }

    // Create tables
    try {
        await pool.query(`

            CREATE TABLE IF NOT EXISTS containers (
                container_id VARCHAR(50) PRIMARY KEY,
                zone VARCHAR(10) NOT NULL,
                width NUMERIC NOT NULL,
                depth NUMERIC NOT NULL,
                height NUMERIC NOT NULL,
                remaining_volume NUMERIC NOT NULL DEFAULT width * depth * height,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS items (
                item_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                width NUMERIC NOT NULL,
                depth NUMERIC NOT NULL,
                height NUMERIC NOT NULL,
                priority INTEGER NOT NULL,
                expiry_date TIMESTAMP NOT NULL,
                usage_limit INTEGER NOT NULL,
                preferred_zone VARCHAR(20),
                container_id VARCHAR(50),
                final_priority INTEGER NOT NULL DEFAULT priority,
                FOREIGN KEY (container_id) REFERENCES containers(container_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );            
            
            CREATE TABLE IF NOT EXISTS placements (
                item_id VARCHAR(50) PRIMARY KEY,
                container_id VARCHAR(50) NOT NULL,
                xi NUMERIC NOT NULL,    -- starting coordinates
                yi NUMERIC NOT NULL,
                zi NUMERIC NOT NULL,
                xj NUMERIC NOT NULL,    -- ending coordinates
                yj NUMERIC NOT NULL,
                zj NUMERIC NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(item_id),
                FOREIGN KEY (container_id) REFERENCES containers(container_id)
            );

            CREATE TABLE IF NOT EXISTS systemlogs (
                log_id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                item_id VARCHAR(50),
                user_id VARCHAR(50),
                from_container_id VARCHAR(50),
                to_container_id VARCHAR(50),
                actionType VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );            
            
            CREATE TABLE IF NOT EXISTS waste (
                waste_id SERIAL PRIMARY KEY,
                item_id VARCHAR(50) NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                reason TEXT NOT NULL,
                container_id VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(item_id),
                FOREIGN KEY (container_id) REFERENCES containers(container_id)
            );
        `);
        console.log('Database and tables initialized successfully');
    } catch (error) {
        console.error('Error creating tables:', error);
    }
};

export { pool, initDatabase };

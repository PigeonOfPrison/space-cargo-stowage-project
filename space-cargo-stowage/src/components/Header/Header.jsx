import React, { useState, useEffect } from 'react';
import './header.css';

function Header() {
    const [dateTime, setDateTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => {
            setDateTime(new Date());
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const formatDate = (date) => {
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const formatTime = (date) => {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    return (
        <header className="header">
            <div className="header-left">
                <h1>Space Cargo Stowage</h1>
            </div>
            <div className="header-right">
                <div className="datetime-display">
                    <div className="date">{formatDate(dateTime)}</div>
                    <div className="time">{formatTime(dateTime)}</div>
                </div>
            </div>
        </header>
    );
}

export default Header;
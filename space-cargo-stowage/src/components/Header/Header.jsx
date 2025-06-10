import React, { useState, useEffect } from 'react';
import { FaRocket } from 'react-icons/fa';
import '../../styles/header1.css';  // New Design System (was "./header.css")

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
        });    };    return (
        <header className="main-container content-container" id="main-header">
            <div className="section-container">
                {/* Brand Section */}
                <div className="brand-section" id="header-brand">
                    <div className="header-logo-container">
                        <FaRocket />
                    </div>
                    <div className="header-brand-text">
                        <div className="header-title">Space Cargo</div>
                        <div className="header-subtitle">Stowage System</div>
                    </div>
                </div>
                
                {/* DateTime Section */}
                <div className="nav-section" id="header-nav">
                    <div className="datetime-container" id="datetime-display">
                        <div className="date-text">{formatDate(dateTime)}</div>
                        <div className="time-text">{formatTime(dateTime)}</div>
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
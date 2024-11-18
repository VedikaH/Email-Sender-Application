// src/components/NavigationBar.js
import React from 'react';
import { Link } from 'react-router-dom';

const NavigationBar = () => {
    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light">
            <div className="container-fluid">
                <Link className="navbar-brand" to="/">Email Sender</Link>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav">
                        <li className="nav-item">
                            <Link className="nav-link" to="/send-email">Send Email</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to="/send-bulk-emails">Send Bulk Emails</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to="/generate-and-send">Generate and Send Email</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to="/generate-and-send-bulk">Generate and Send Bulk Emails</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to="/analytics">Analytics</Link>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
};

export default NavigationBar;
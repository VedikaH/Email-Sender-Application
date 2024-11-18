// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import EmailForm from './components/EmailForm';
//import Statistics from './components/Statistics';
import GenerateAndSendEmailForm from './components/GenerateAndSendEmailForm';
import SendBulkEmailsForm from './components/SendBulkEmailsForm';
import GenerateAndSendBulkEmailsForm from './components/GenerateAndSendBulkEmailsForm';
import Analytics from './components/Analytics';

const App = () => {
    return (
        <Router>
            <div className="container mt-5">
                <NavigationBar />
                <Routes>
                    <Route path="/" element={<h1 className="text-center">Welcome to the Email Sender Application</h1>} />
                    <Route path="/send-email" element={<EmailForm />} />
                    <Route path="/send-bulk-emails" element={<SendBulkEmailsForm />} />
                    <Route path="/generate-and-send" element={<GenerateAndSendEmailForm />} />
                    <Route path="/generate-and-send-bulk" element={<GenerateAndSendBulkEmailsForm />} />
                    <Route path="/analytics" element={<Analytics />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
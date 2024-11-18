// src/components/EmailForm.js
import React, { useState } from 'react';
import { sendEmail } from '../api';

const EmailForm = () => {
    const [toAddresses, setToAddresses] = useState('');
    const [subject, setSubject] = useState('');
    const [bodyHtml, setBodyHtml] = useState('');
    const [bodyText, setBodyText] = useState('');
    const [scheduledTime, setScheduledTime] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const emailData = {
            to_addresses: toAddresses.split(',').map(email => email.trim()),
            subject,
            body_html: bodyHtml,
            body_text: bodyText,
            scheduled_time: scheduledTime ? new Date(scheduledTime) : null, // Convert to Date object if provided
        };

        try {
            const response = await sendEmail(emailData);
            alert('Email sent successfully!');
        } catch (error) {
            alert('Error sending email: ' + error.message);
        }
    };

    return (
        <div className="mb-4">
            <h2>Send Email</h2>
            <form onSubmit={handleSubmit} className="border p-4 rounded shadow">
                <div className="form-group">
                    <label>To Addresses (comma separated)</label>
                    <input
                        type="text"
                        className="form-control"
                        value={toAddresses}
                        onChange={(e) => setToAddresses(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Subject</label>
                    <input
                        type="text"
                        className="form-control"
                        value={subject}
                        onChange={(e) => setSubject(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Body HTML</label>
                    <textarea
                        className="form-control"
                        value={bodyHtml}
                        onChange={(e) => setBodyHtml(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Body Text (optional)</label>
                    <textarea
                        className="form-control"
                        value={bodyText}
                        onChange={(e) => setBodyText(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label>Scheduled Time (optional)</label>
                    <input
                        type="datetime-local"
                        className="form-control"
                        value={scheduledTime}
                        onChange={(e) => setScheduledTime(e.target.value)}
                    />
                </div>
                <button type="submit" className="btn btn-primary">Send Email</button>
            </form>
        </div>
    );
};

export default EmailForm;
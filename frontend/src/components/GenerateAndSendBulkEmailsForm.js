import React, { useState } from 'react';
import { generateAndSendBulkEmail } from '../api';

const GenerateAndSendBulkEmailsForm = () => {
    const [file, setFile] = useState(null);
    const [situation, setSituation] = useState('');
    const [keywords, setKeywords] = useState('');
    const [recipientColumn, setRecipientColumn] = useState('');
    const [scheduledTime, setScheduledTime] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', file);
        formData.append('situation', situation);
        formData.append('keywords', keywords.split(',').map(keyword => keyword.trim()));
        formData.append('recipient_column', recipientColumn);
        formData.append('scheduled_time', scheduledTime ? new Date(scheduledTime).toISOString() : null);

        try {
            const response = await generateAndSendBulkEmail(formData);
            alert(`Bulk emails processed successfully!`);
        } catch (error) {
            alert('Error generating and sending bulk emails: ' + error.message);
        }
    };

    return (
        <div className="mb-4">
            <h2>Generate and Send Bulk Emails</h2>
            <form onSubmit={handleSubmit} className="border p-4 rounded shadow">
                <div className="form-group">
                    <label>CSV File</label>
                    <input
                        type="file"
                        className="form-control"
                        accept=".csv"
                        onChange={(e) => setFile(e.target.files[0])}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Situation</label>
                    <input
                        type="text"
                        className="form-control"
                        value={situation}
                        onChange={(e) => setSituation(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Keywords (comma separated)</label>
                    <input
                        type="text"
                        className="form-control"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Recipient Column Name</label>
                    <input
                        type="text"
                        className="form-control"
                        value={recipientColumn}
                        onChange={(e) => setRecipientColumn(e.target.value)}
                        placeholder="Enter the column name containing email addresses"
                        required
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
                <button type="submit" className="btn btn-primary">
                    Generate and Send Bulk Emails
                </button>
            </form>
        </div>
    );
};

export default GenerateAndSendBulkEmailsForm;
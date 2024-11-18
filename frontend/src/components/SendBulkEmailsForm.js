import React, { useState } from 'react';
import { SendBulkEmails } from '../api';

const SendBulkEmailsForm = () => {
    const [file, setFile] = useState(null);
    const [template, setTemplate] = useState('');
    const [subjectTemplate, setSubjectTemplate] = useState('');
    const [placeholderColumns, setPlaceholderColumns] = useState('');
    const [recipientColumn, setRecipientColumn] = useState('');
    const [scheduledTime, setScheduledTime] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const params = new URLSearchParams();
            params.append('template', template);
            params.append('subject_template', subjectTemplate);
            params.append('placeholder_columns', placeholderColumns);
            params.append('recipient_column', recipientColumn);
            if (scheduledTime) {
                params.append('scheduled_time', scheduledTime);
            }

            const formData = new FormData();
            formData.append('file', file);

            const url = `http://localhost:8000/csv/send-bulk-emails?${params.toString()}`;

            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to send emails');
            }

            const result = await response.json();
            alert('Bulk emails generated and sent successfully!');
        } catch (error) {
            setError(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="mb-4">
            <h2>Send Bulk Emails</h2>
            <form onSubmit={handleSubmit} className="border p-4 rounded shadow">
                {error && (
                    <div className="alert alert-danger" role="alert">
                        {error}
                    </div>
                )}
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
                    <label>Email Template</label>
                    <textarea
                        className="form-control"
                        value={template}
                        onChange={(e) => setTemplate(e.target.value)}
                        placeholder="Dear {Name}, welcome to {Company}..."
                        rows={4}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Subject Template</label>
                    <input
                        type="text"
                        className="form-control"
                        value={subjectTemplate}
                        onChange={(e) => setSubjectTemplate(e.target.value)}
                        placeholder="Welcome to {Company}, {Name}!"
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Placeholder Columns</label>
                    <input
                        type="text"
                        className="form-control"
                        value={placeholderColumns}
                        onChange={(e) => setPlaceholderColumns(e.target.value)}
                        placeholder="Name,Company"
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Recipient Column</label>
                    <input
                        type="text"
                        className="form-control"
                        value={recipientColumn}
                        onChange={(e) => setRecipientColumn(e.target.value)}
                        placeholder="Email"
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
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isLoading}
                >
                    {isLoading ? 'Sending...' : 'Send Bulk Emails'}
                </button>
            </form>
        </div>
    );
};

export default SendBulkEmailsForm;

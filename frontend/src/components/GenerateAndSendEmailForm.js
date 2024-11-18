import React, { useState } from 'react';
import { generateAndSendEmail } from '../api';

const GenerateAndSendEmailForm = () => {
    const [toAddresses, setToAddresses] = useState('');
    const [emailType, setEmailType] = useState('');
    const [situation, setSituation] = useState('');
    const [keywords, setKeywords] = useState('');
    const [scheduledTime, setScheduledTime] = useState('');
    
    // Template data fields
    const [templateFields, setTemplateFields] = useState([
        { key: '', value: '' }
    ]);

    const handleTemplateFieldChange = (index, field, value) => {
        const newFields = [...templateFields];
        newFields[index][field] = value;
        setTemplateFields(newFields);
    };

    const addTemplateField = () => {
        setTemplateFields([...templateFields, { key: '', value: '' }]);
    };

    const removeTemplateField = (index) => {
        const newFields = templateFields.filter((_, i) => i !== index);
        setTemplateFields(newFields);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Convert template fields to object
        const templateData = templateFields.reduce((acc, field) => {
            if (field.key && field.value) {
                acc[field.key] = field.value;
            }
            return acc;
        }, {});

        const emailData = {
            to_addresses: toAddresses.split(',').map(email => email.trim()),
            email_type: emailType,
            situation,
            keywords: keywords.split(',').map(keyword => keyword.trim()),
            template_data: templateData,
            scheduled_time: scheduledTime ? new Date(scheduledTime) : null,
        };

        try {
            const response = await generateAndSendEmail(emailData);
            alert('Emails generated and sent successfully!');
        } catch (error) {
            alert('Error generating and sending emails: ' + error.message);
        }
    };

    return (
        <div className="container">
            <h2 className="mb-4">Generate and Send Email</h2>
            <form onSubmit={handleSubmit}>
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
                    <label>Email Type</label>
                    <input
                        type="text"
                        className="form-control"
                        value={emailType}
                        onChange={(e) => setEmailType(e.target.value)}
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
                    <label>Template Data Fields</label>
                    {templateFields.map((field, index) => (
                        <div key={index} className="form-row mb-2">
                            <div className="col">
                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="Field name"
                                    value={field.key}
                                    onChange={(e) => handleTemplateFieldChange(index, 'key', e.target.value)}
                                />
                            </div>
                            <div className="col">
                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="Field value"
                                    value={field.value}
                                    onChange={(e) => handleTemplateFieldChange(index, 'value', e.target.value)}
                                />
                            </div>
                            <div className="col-auto">
                                <button
                                    type="button"
                                    className="btn btn-danger"
                                    onClick={() => removeTemplateField(index)}
                                >
                                    Remove
                                </button>
                            </div>
                        </div>
                    ))}
                    <button
                        type="button"
                        className="btn btn-secondary mt-2"
                        onClick={addTemplateField}
                    >
                        Add Field
                    </button>
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
                    Generate and Send Email
                </button>
            </form>
        </div>
    );
};

export default GenerateAndSendEmailForm;
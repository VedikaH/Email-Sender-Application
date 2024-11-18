
// src/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Replace with your actual API URL

export const sendEmail = async (emailData) => {
    return await axios.post(`${API_URL}/email/send`, emailData);
};

export const generateAndSendEmail = async (data) => {
    return await axios.post(`${API_URL}/email/generate-and-send`, data);
};

export const verifyEmail = async (email) => {
    return await axios.post(`${API_URL}/email/verify-email`, { email });
};

export const getStatistics = async () => {
    return await axios.get(`${API_URL}/email/statistics`);
};

export const SendBulkEmails = async (formData) => {
    return await axios.post(`${API_URL}/csv/send-bulk-emails`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};

export const generateAndSendBulkEmail = async (data) => {
    return await axios.post(`${API_URL}/email/generate-and-send-bulk`, data);
};

export const fetchAnalytics = async () => {
    try {
        const response = await fetch(`${API_URL}/analytics/analytics`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // Add any authentication headers if needed
                // 'Authorization': `Bearer ${token}`
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};
// Add other API functions as needed
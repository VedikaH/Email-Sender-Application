import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Clock, CheckCircle, XCircle } from 'lucide-react';
import { fetchAnalytics } from '../api';

const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const Card = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
`;

const StatusCard = styled(Card)`
  display: flex;
  align-items: center;
  gap: 16px;
  
  .icon-wrapper {
    padding: 12px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.green { background: #dcfce7; }
    &.yellow { background: #fef9c3; }
    &.blue { background: #dbeafe; }
    &.red { background: #fee2e2; }
  }
  
  .content {
    flex: 1;
    
    h3 {
      font-size: 14px;
      color: #6b7280;
      margin: 0;
    }
    
    .value {
      font-size: 24px;
      font-weight: 600;
      margin: 0;
    }
  }
`;

const ChartGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
`;

const ChartCard = styled(Card)`
  h2 {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 20px 0;
  }
`;

const MetricsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MetricItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .label {
    font-size: 14px;
    color: #6b7280;
  }
  
  .value {
    font-size: 18px;
    font-weight: 600;
    
    &.success { color: #059669; }
    &.error { color: #dc2626; }
    &.warning { color: #d97706; }
  }
`;

const LoadingState = styled.div`
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: 18px;
`;

const ErrorState = styled(LoadingState)`
  flex-direction: column;
  gap: 16px;
  
  .error-message {
    color: #dc2626;
  }
  
  .sub-message {
    font-size: 14px;
  }
  
  button {
    padding: 8px 16px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    
    &:hover {
      background: #2563eb;
    }
  }
`;

const Analytics = () => {
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getAnalyticsData = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await fetchAnalytics();
                setData(response);
            } catch (err) {
                setError(err.message);
                console.error('Error fetching analytics:', err);
            } finally {
                setIsLoading(false);
            }
        };

        getAnalyticsData();
    }, []);

    if (isLoading) {
        return <LoadingState>Loading analytics...</LoadingState>;
    }

    if (error) {
        return (
            <ErrorState>
                <div className="error-message">Error loading analytics</div>
                <div className="sub-message">{error}</div>
                <button onClick={() => window.location.reload()}>Retry</button>
            </ErrorState>
        );
    }

    if (!data || !data.database_metrics || !data.ses_metrics) {
        return <LoadingState>No analytics data available</LoadingState>;
    }

    const { database_metrics, ses_metrics } = data;

    const statusData = [
        {
            title: 'Sent',
            value: database_metrics.status_breakdown.sent,
            icon: CheckCircle,
            colorClass: 'green'
        },
        {
            title: 'Pending',
            value: database_metrics.status_breakdown.pending,
            icon: Clock,
            colorClass: 'yellow'
        },
        {
            title: 'Scheduled',
            value: database_metrics.status_breakdown.scheduled,
            icon: Activity,
            colorClass: 'blue'
        },
        {
            title: 'Failed',
            value: database_metrics.status_breakdown.failed,
            icon: XCircle,
            colorClass: 'red'
        }
    ];

    const deliveryData = [
        {
            name: 'Successful',
            value: ses_metrics.overall_stats.total_delivery_attempts -
                   ses_metrics.overall_stats.total_bounces -
                   ses_metrics.overall_stats.total_rejects
        },
        {
            name: 'Bounced',
            value: ses_metrics.overall_stats.total_bounces
        },
        {
            name: 'Rejected',
            value: ses_metrics.overall_stats.total_rejects
        }
    ];

    return (
        <Container>
            <StatusGrid>
                {statusData.map((item) => (
                    <StatusCard key={item.title}>
                        <div className={`icon-wrapper ${item.colorClass}`}>
                            <item.icon size={24} />
                        </div>
                        <div className="content">
                            <h3>{item.title}</h3>
                            <p className="value">{item.value.toLocaleString()}</p>
                        </div>
                    </StatusCard>
                ))}
            </StatusGrid>

            <ChartGrid>
                <ChartCard>
                    <h2>Delivery Statistics</h2>
                    <div style={{ height: 300 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={deliveryData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="value" fill="#4f46e5" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>

                <ChartCard>
                    <h2>Key Metrics</h2>
                    <MetricsList>
                        <MetricItem>
                            <span className="label">Success Rate</span>
                            <span className="value success">
                                {ses_metrics.overall_stats.success_rate}%
                            </span>
                        </MetricItem>
                        <MetricItem>
                            <span className="label">Bounce Rate</span>
                            <span className="value error">
                                {ses_metrics.overall_stats.bounce_rate}%
                            </span>
                        </MetricItem>
                        <MetricItem>
                            <span className="label">Total Complaints</span>
                            <span className="value warning">
                                {ses_metrics.overall_stats.total_complaints}
                            </span>
                        </MetricItem>
                        <MetricItem>
                            <span className="label">Total Emails</span>
                            <span className="value">
                                {database_metrics.total_emails.toLocaleString()}
                            </span>
                        </MetricItem>
                    </MetricsList>
                </ChartCard>
            </ChartGrid>
        </Container>
    );
};

export default Analytics;
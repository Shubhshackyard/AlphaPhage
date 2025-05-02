import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AlertCard from './AlertCard';
import TopicTrend from './TopicTrend';
import config from '../config';

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('all');

  // Calculate max volume for topic trend visualization
  const maxVolume = topics.length > 0 
    ? Math.max(...topics.map(topic => topic.volume)) 
    : 0;

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch alerts and topics in parallel
        const [alertsResponse, topicsResponse] = await Promise.all([
          axios.get(`${config.API_URL}/api/v1/alerts`),
          axios.get(`${config.API_URL}/api/v1/topics`)
        ]);
        
        setAlerts(alertsResponse.data);
        setTopics(topicsResponse.data);
        setError(null);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    // Initial data fetch
    fetchData();
    
    // Set up polling for new data every minute
    const interval = setInterval(fetchData, 60000);
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, []);
  
  // Filter alerts by severity
  const filteredAlerts = severityFilter === 'all' 
    ? alerts 
    : alerts.filter(alert => alert.severity.toLowerCase() === severityFilter);

  // Render loading state
  if (loading && !alerts.length && !topics.length) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">AlphaPhage Dashboard</h1>
        <p className="text-gray-600">Real-time narrative mining for financial signals</p>
      </header>
      
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Alerts Section */}
        <div className="lg:col-span-2">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Latest Alerts</h2>
              <div>
                <select 
                  className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2"
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                >
                  <option value="all">All Severities</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
            
            {filteredAlerts.length > 0 ? (
              filteredAlerts.map(alert => (
                <AlertCard key={alert.alert_id} alert={alert} />
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">No alerts to display</p>
            )}
          </div>
        </div>
        
        {/* Topics Section */}
        <div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Trending Topics</h2>
            
            {topics.length > 0 ? (
              topics.map(topic => (
                <TopicTrend 
                  key={topic.topic_id} 
                  topic={topic} 
                  maxVolume={maxVolume} 
                />
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">No topics to display</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
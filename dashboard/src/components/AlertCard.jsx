import React from 'react';
import PropTypes from 'prop-types';

const AlertCard = ({ alert }) => {
  // Map severity to color
  const getSeverityColor = (severity) => {
    switch (severity.toUpperCase()) {
      case 'HIGH':
        return 'bg-red-100 border-red-500 text-red-700';
      case 'MEDIUM':
        return 'bg-yellow-100 border-yellow-500 text-yellow-700';
      case 'LOW':
        return 'bg-blue-100 border-blue-500 text-blue-700';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-700';
    }
  };
  
  // Format the alert time
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Calculate percentage increase
  const percentageIncrease = alert.volume && alert.expected_volume 
    ? Math.round((alert.volume / alert.expected_volume - 1) * 100) 
    : 0;

  return (
    <div className={`rounded-lg border-l-4 p-4 mb-4 shadow-md ${getSeverityColor(alert.severity)}`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold text-lg">{alert.topic_label}</h3>
          <p className="text-sm">{alert.alert_message}</p>
        </div>
        <span className="bg-white text-sm font-semibold px-2.5 py-0.5 rounded shadow">
          {alert.severity}
        </span>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
        <div>
          <span className="font-medium">Volume:</span> 
          <span className="ml-1">{alert.volume}</span>
        </div>
        <div>
          <span className="font-medium">Expected:</span> 
          <span className="ml-1">{Math.round(alert.expected_volume)}</span>
        </div>
        <div>
          <span className="font-medium">Increase:</span>
          <span className={`ml-1 ${percentageIncrease > 100 ? 'text-red-600 font-bold' : 'text-red-500'}`}>
            +{percentageIncrease}%
          </span>
        </div>
      </div>
      
      <div className="flex justify-between items-center mt-3 text-sm">
        <div className="font-medium">
          <span>Z-Score: </span>
          <span className="font-bold">{alert.z_score.toFixed(2)}</span>
        </div>
        <div className="text-right text-xs opacity-75">
          {formatTime(alert.alert_time)}
        </div>
      </div>
    </div>
  );
};

AlertCard.propTypes = {
  alert: PropTypes.shape({
    topic_label: PropTypes.string.isRequired,
    alert_message: PropTypes.string.isRequired,
    severity: PropTypes.string.isRequired,
    volume: PropTypes.number.isRequired,
    expected_volume: PropTypes.number.isRequired,
    z_score: PropTypes.number.isRequired,
    alert_time: PropTypes.string.isRequired
  }).isRequired
};

export default AlertCard;
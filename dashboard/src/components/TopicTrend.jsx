import React from 'react';
import PropTypes from 'prop-types';

const TopicTrend = ({ topic, maxVolume }) => {
  // Calculate percentage of max volume for bar width
  const percentageOfMax = maxVolume > 0 ? (topic.volume / maxVolume) * 100 : 0;

  // Format the last updated timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-medium text-lg">{topic.topic_label}</h3>
        <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded">
          ID: {topic.topic_id}
        </span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className="bg-blue-600 h-2.5 rounded-full" 
          style={{ width: `${percentageOfMax}%` }}>
        </div>
      </div>
      
      <div className="flex justify-between items-center mt-2">
        <span className="text-sm font-medium">Volume: {topic.volume}</span>
        <span className="text-xs text-gray-500">
          Last updated: {formatTime(topic.last_updated)}
        </span>
      </div>
    </div>
  );
};

TopicTrend.propTypes = {
  topic: PropTypes.shape({
    topic_id: PropTypes.number.isRequired,
    topic_label: PropTypes.string.isRequired,
    volume: PropTypes.number.isRequired,
    last_updated: PropTypes.string.isRequired
  }).isRequired,
  maxVolume: PropTypes.number.isRequired
};

export default TopicTrend;
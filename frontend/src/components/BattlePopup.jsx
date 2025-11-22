import React from 'react';
import './BattlePopup.css';

const BattlePopup = ({ battle }) => {
  if (!battle) return null;

  const formatDate = (startDate, endDate) => {
    if (!startDate && !endDate) return 'Date unknown';
    if (startDate && endDate) {
      if (startDate === endDate) return startDate;
      return `${startDate} - ${endDate}`;
    }
    return startDate || endDate;
  };

  const getParticipants = (sidesInvolved) => {
    if (!sidesInvolved || sidesInvolved.length === 0) return 'Unknown';
    return sidesInvolved.join(', ');
  };

  return (
    <div className="battle-popup">
      <h3>{battle.name}</h3>
      <div className="popup-details">
        <div className="detail-row">
          <span className="label">Date:</span>
          <span className="value">{formatDate(battle.start_date, battle.end_date)}</span>
        </div>
        <div className="detail-row">
          <span className="label">Period:</span>
          <span className="value">{battle.war_period || 'Unknown'}</span>
        </div>
        {battle.outcome && (
          <div className="detail-row">
            <span className="label">Outcome:</span>
            <span className="value">{battle.outcome}</span>
          </div>
        )}
        <div className="detail-row">
          <span className="label">Participants:</span>
          <span className="value">{getParticipants(battle.sides_involved)}</span>
        </div>
        {battle.casualties_estimated && (
          <div className="detail-row">
            <span className="label">Casualties:</span>
            <span className="value">{battle.casualties_estimated.toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default BattlePopup;

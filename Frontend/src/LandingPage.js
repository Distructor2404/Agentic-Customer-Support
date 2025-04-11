import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css'; // Optional CSS

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      <h1>Welcome to Agentic Support Portal</h1>
      <div className="button-group">
        <button onClick={() => navigate('/raise-ticket')}>Raise a Ticket</button>
        <button onClick={() => navigate('/section')}>Agentic FAQs</button>
      </div>
    </div>
  );
}

export default LandingPage;
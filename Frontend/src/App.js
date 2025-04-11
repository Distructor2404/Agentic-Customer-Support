import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import RaiseTicket from './RaiseTicket';
import Section from './Section';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/raise-ticket" element={<RaiseTicket />} />
        <Route path="/section" element={<Section />} />
      </Routes>
    </Router>
  );
}

export default App;
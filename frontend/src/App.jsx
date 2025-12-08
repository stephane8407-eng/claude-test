import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Map from './components/Map';
import ProjectKanbanPage from './pages/admin/ProjectKanbanPage';
import './App.css';
import './components/grants/grants.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Map />} />
          <Route path="/dashboard/projects" element={<ProjectKanbanPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

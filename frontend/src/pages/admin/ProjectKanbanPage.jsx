import React from 'react';
import ProjectKanban from '../../components/dashboard/ProjectKanban';
import '../../components/dashboard/ProjectKanban.css';

export default function ProjectKanbanPage() {
  // For now, hardcode Chirac slug - later can get from URL params
  const villageSlug = 'chirac';

  return (
    <div className="project-management-page">
      <div className="dashboard-header">
        <h1>Project Management</h1>
        <p>Track and manage your village projects</p>
      </div>

      <ProjectKanban villageSlug={villageSlug} />
    </div>
  );
}

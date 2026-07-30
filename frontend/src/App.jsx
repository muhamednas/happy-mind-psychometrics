import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Layouts
import Layout from './components/Layout';
import PortalLayout from './components/PortalLayout';

// Admin Pages
import Dashboard from './pages/admin/Dashboard';
import PackageBuilder from './pages/admin/PackageBuilder';
import CandidateTracker from './pages/admin/CandidateTracker';

// Portal Pages
import Login from './pages/portal/Login';
import TestDashboard from './pages/portal/TestDashboard';
import TestRunner from './pages/portal/TestRunner';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Root redirect */}
        <Route path="/" element={<Navigate to="/admin" replace />} />

        {/* Admin Routes */}
        <Route path="/admin" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="packages/create" element={<PackageBuilder />} />
          <Route path="candidates" element={<CandidateTracker />} />
        </Route>

        {/* Portal Routes */}
        <Route path="/portal" element={<PortalLayout />}>
          <Route index element={<Login />} />
          <Route path="dashboard" element={<TestDashboard />} />
          <Route path="test/:testId" element={<TestRunner />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

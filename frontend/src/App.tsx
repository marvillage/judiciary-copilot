import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Auth from './pages/Auth'
import Dashboard from './pages/Dashboard'
import Landing from './pages/Landing'
import ModulePlaceholder from './pages/ModulePlaceholder'
import { modules } from './data/modules'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Auth mode="login" />} />
      <Route path="/signup" element={<Auth mode="signup" />} />
      <Route path="/app" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="matters" element={<Dashboard />} />
        {modules.map((m) => (
          <Route key={m.path} path={m.path.replace('/app/', '')} element={<ModulePlaceholder module={m} />} />
        ))}
        <Route path="*" element={<Navigate to="/app" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

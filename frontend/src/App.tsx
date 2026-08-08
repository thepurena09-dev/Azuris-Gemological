import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "@/App.css";

import PublicLayout from "@/layouts/PublicLayout";
import AdminLayout from "@/layouts/AdminLayout";

import HomePage from "@/pages/public/HomePage";
import AboutPage from "@/pages/public/AboutPage";
import ContactPage from "@/pages/public/ContactPage";
import LegalityPage from "@/pages/public/LegalityPage";
import LoginPage from "@/pages/auth/LoginPage";
import DashboardPage from "@/pages/admin/DashboardPage";
import NotFoundPage from "@/pages/NotFoundPage";

function App() {
  return (
    <div className="App min-h-screen bg-background text-foreground">
      <BrowserRouter>
        <Routes>
          {/* Public shell */}
          <Route element={<PublicLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/legalitas" element={<LegalityPage />} />

            {/* Certification repositioning — verification lives on the homepage */}
            <Route path="/verification" element={<Navigate to="/#verification" replace />} />
            {/* Public catalog removed — legacy routes redirect to homepage (no data deleted) */}
            <Route path="/catalog" element={<Navigate to="/" replace />} />
            <Route path="/catalog/gemstones" element={<Navigate to="/" replace />} />
            <Route path="/catalog/jewelry" element={<Navigate to="/" replace />} />
          </Route>

          {/* Authentication */}
          <Route path="/login" element={<LoginPage />} />

          {/* Admin shell */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;

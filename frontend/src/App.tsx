import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "@/App.css";

import PublicLayout from "@/layouts/PublicLayout";
import AdminLayout from "@/layouts/AdminLayout";

import HomePage from "@/pages/public/HomePage";
import AboutPage from "@/pages/public/AboutPage";
import VerificationPage from "@/pages/public/VerificationPage";
import CatalogPage from "@/pages/public/CatalogPage";
import GemstonesPage from "@/pages/public/GemstonesPage";
import JewelryPage from "@/pages/public/JewelryPage";
import ContactPage from "@/pages/public/ContactPage";
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
            <Route path="/verification" element={<VerificationPage />} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/catalog/gemstones" element={<GemstonesPage />} />
            <Route path="/catalog/jewelry" element={<JewelryPage />} />
            <Route path="/contact" element={<ContactPage />} />
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

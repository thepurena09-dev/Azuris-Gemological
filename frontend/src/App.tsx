import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "@/App.css";

import { AuthProvider, useAuth } from "@/lib/auth";
import { BusinessSettingsProvider } from "@/lib/settings";

import PublicLayout from "@/layouts/PublicLayout";
import AdminLayout from "@/layouts/AdminLayout";

import HomePage from "@/pages/public/HomePage";
import AboutPage from "@/pages/public/AboutPage";
import ContactPage from "@/pages/public/ContactPage";
import LegalityPage from "@/pages/public/LegalityPage";
import LoginPage from "@/pages/auth/LoginPage";
import DashboardPage from "@/pages/admin/DashboardPage";
import LegalityAdminPage from "@/pages/admin/LegalityAdminPage";
import SettingsPage from "@/pages/admin/SettingsPage";
import CertificatesPage from "@/pages/admin/CertificatesPage";
import GemstonesPage from "@/pages/admin/GemstonesPage";
import JewelryPage from "@/pages/admin/JewelryPage";
import WarrantiesPage from "@/pages/admin/WarrantiesPage";
import VisualsPage from "@/pages/admin/VisualsPage";
import VerifyPage from "@/pages/public/VerifyPage";
import NotFoundPage from "@/pages/NotFoundPage";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { admin, ready } = useAuth();
  if (!ready) return null;
  if (!admin) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function App() {
  return (
    <div className="App min-h-screen bg-background text-foreground">
      <BrowserRouter>
        <AuthProvider>
          <BusinessSettingsProvider>
            <Routes>
              {/* Public shell */}
              <Route element={<PublicLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/contact" element={<ContactPage />} />
                <Route path="/legalitas" element={<LegalityPage />} />
                <Route path="/verify" element={<VerifyPage />} />

                <Route path="/verification" element={<Navigate to="/verify" replace />} />
                <Route path="/membership" element={<Navigate to="/verify" replace />} />
                <Route path="/catalog" element={<Navigate to="/" replace />} />
                <Route path="/catalog/gemstones" element={<Navigate to="/" replace />} />
                <Route path="/catalog/jewelry" element={<Navigate to="/" replace />} />
              </Route>

              {/* Authentication */}
              <Route path="/login" element={<LoginPage />} />

              {/* Admin shell (protected) */}
              <Route
                path="/admin"
                element={
                  <RequireAuth>
                    <AdminLayout />
                  </RequireAuth>
                }
              >
                <Route index element={<Navigate to="/admin/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="legalitas" element={<LegalityAdminPage />} />
                <Route path="certificates" element={<CertificatesPage />} />
                <Route path="gemstones" element={<GemstonesPage />} />
                <Route path="jewelry" element={<JewelryPage />} />
                <Route path="warranties" element={<WarrantiesPage />} />
                <Route path="visuals" element={<VisualsPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>

              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BusinessSettingsProvider>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;

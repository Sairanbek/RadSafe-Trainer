import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SectionsPage } from "./pages/SectionsPage";
import { SubsectionsPage } from "./pages/SubsectionsPage";
import { TestPage } from "./pages/TestPage";
import { SummaryPage } from "./pages/SummaryPage";
import { StatsPage } from "./pages/StatsPage";
import { HistoryPage } from "./pages/HistoryPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { ProfilePage } from "./pages/ProfilePage";
import { AdminQuestionsPage } from "./pages/AdminQuestionsPage";
import { AdminQuestionFormPage } from "./pages/AdminQuestionFormPage";
import { AIAssistantPage } from "./pages/AIAssistantPage";
import { PrivacyPolicyPage } from "./pages/PrivacyPolicyPage";
import { VerifyEmailPage } from "./pages/VerifyEmailPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/training/sections"
            element={
              <ProtectedRoute>
                <SectionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/training/sections/:section/subsections"
            element={
              <ProtectedRoute>
                <SubsectionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/test/:sessionId"
            element={
              <ProtectedRoute>
                <TestPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/test/:sessionId/summary"
            element={
              <ProtectedRoute>
                <SummaryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/stats"
            element={
              <ProtectedRoute>
                <StatsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <HistoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assistant"
            element={
              <ProtectedRoute>
                <AIAssistantPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/questions"
            element={
              <ProtectedRoute>
                <AdminQuestionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/questions/:id"
            element={
              <ProtectedRoute>
                <AdminQuestionFormPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { MainLayout } from './layouts/MainLayout';
import { Login } from './pages/Login';
import { ExecutiveOverview } from './pages/ExecutiveOverview';
import { DataQuality } from './pages/DataQuality';
import { Settings } from './pages/Settings';
import { SalesIntelligence } from './pages/SalesIntelligence';
import { CustomerIntelligence } from './pages/CustomerIntelligence';
import { RFMSegmentation } from './pages/RFMSegmentation';
import { CustomerEngagementRisk } from './pages/CustomerEngagementRisk';
import { ProductIntelligence } from './pages/ProductIntelligence';
import { SellerAnalytics } from './pages/SellerAnalytics';
import { DeliveryAndSatisfaction } from './pages/DeliveryAndSatisfaction';
import { PaymentIntelligence } from './pages/PaymentIntelligence';
import { SalesForecast } from './pages/SalesForecast';
import { ModelPerformance } from './pages/ModelPerformance';
import { DataExplorer } from './pages/DataExplorer';
import { BusinessInsights } from './pages/BusinessInsights';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-xs font-mono">
        Authenticating session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* Protected Platform Shell */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            {/* 1. Executive Overview */}
            <Route index element={<ExecutiveOverview />} />

            {/* 2. Sales Intelligence */}
            <Route path="sales" element={<SalesIntelligence />} />

            {/* 3. Customer Intelligence */}
            <Route path="customers" element={<CustomerIntelligence />} />

            {/* 4. RFM Segmentation */}
            <Route path="rfm" element={<RFMSegmentation />} />

            {/* 5. Customer Engagement Risk */}
            <Route path="customer-risk" element={<CustomerEngagementRisk />} />

            {/* 6. Product Intelligence */}
            <Route path="products" element={<ProductIntelligence />} />

            {/* 7. Seller Intelligence */}
            <Route path="sellers" element={<SellerAnalytics />} />

            {/* 8. Delivery & Satisfaction */}
            <Route path="delivery" element={<DeliveryAndSatisfaction />} />

            {/* 9. Payment Intelligence */}
            <Route path="payments" element={<PaymentIntelligence />} />

            {/* 10. Forecasting */}
            <Route path="forecasting" element={<SalesForecast />} />

            {/* 11. Model Performance */}
            <Route path="model-performance" element={<ModelPerformance />} />

            {/* 12. Data Quality (Live) */}
            <Route path="data-quality" element={<DataQuality />} />

            {/* 13. Data Explorer */}
            <Route path="data-explorer" element={<DataExplorer />} />

            {/* 14. Business Insights */}
            <Route path="insights" element={<BusinessInsights />} />

            {/* 15. Settings */}
            <Route path="settings" element={<Settings />} />
          </Route>

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

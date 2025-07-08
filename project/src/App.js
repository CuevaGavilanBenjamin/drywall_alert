import React, { useState } from 'react';
import BankHeader from './components/BankHeader';
import BankSidebar from './components/BankSidebar';
import BankDashboard from './components/BankDashboard';
import BankAccounts from './components/BankAccounts';
import BankTransfers from './components/BankTransfers';
import DryWallMonitor from './components/DryWallMonitor';
import { defaultAccounts, defaultTransactions } from './mock/bankData';

const App = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [userName] = useState('Juan Pérez'); // Simulación de usuario logueado
  const [accounts] = useState(defaultAccounts);
  const [recentTransactions] = useState(defaultTransactions);

  const handleLogout = () => {
    alert('Cerrando sesión...');
    // Aquí iría la lógica real de cierre de sesión
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <BankDashboard accounts={accounts} recentTransactions={recentTransactions} />;
      case 'accounts':
        return <BankAccounts accounts={accounts} />;
      case 'transfers':
        return <BankTransfers accounts={accounts} />;
      case 'payments':
        return <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow"><h2 className="text-3xl font-bold text-gray-800 mb-6">Pagos de Servicios</h2><p className="text-gray-600">Aquí podrás gestionar tus pagos.</p></div>;
      case 'history':
        return <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow"><h2 className="text-3xl font-bold text-gray-800 mb-6">Historial de Movimientos</h2><p className="text-gray-600">Consulta todas tus transacciones pasadas.</p></div>;
      case 'drywall':
        return <DryWallMonitor />;
      default:
        return <BankDashboard accounts={accounts} recentTransactions={recentTransactions} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <BankHeader userName={userName} onLogout={handleLogout} />
      <div className="flex flex-col sm:flex-row flex-grow p-4 sm:p-6 space-y-4 sm:space-y-0 sm:space-x-6">
        <BankSidebar currentPage={currentPage} onNavigate={setCurrentPage} />
        {renderPage()}
      </div>
    </div>
  );
};

export default App;

// DONE
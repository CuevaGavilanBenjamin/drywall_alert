import React from 'react';

const BankSidebar = ({ currentPage, onNavigate }) => {
  const navItems = [
    { name: 'Inicio', page: 'dashboard' },
    { name: 'Cuentas', page: 'accounts' },
    { name: 'Transferencias', page: 'transfers' },
    { name: 'Pagos', page: 'payments' },
    { name: 'Historial', page: 'history' },
    { name: 'DryWall Monitor', page: 'drywall' },
  ];

  return (
    <nav className="w-full sm:w-64 bg-gray-50 p-4 rounded-2xl shadow-lg sm:shadow-none sm:rounded-none">
      <ul className="flex sm:flex-col justify-around sm:justify-start space-x-2 sm:space-x-0 sm:space-y-4">
        {navItems.map((item) => (
          <li key={item.page}>
            <button
              onClick={() => onNavigate(item.page)}
              className={`w-full text-left px-4 py-3 rounded-xl transition-all duration-200 ease-in-out
                ${currentPage === item.page
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-blue-100 hover:text-blue-700'
                }
                flex items-center justify-center sm:justify-start text-sm sm:text-base
              `}
            >
              {/* Iconos SVG simples para cada elemento */}
              {item.name === 'Inicio' && (
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
              )}
              {item.name === 'Cuentas' && (
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
              )}
              {item.name === 'Transferencias' && (
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path></svg>
              )}
              {item.name === 'Pagos' && (
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
              )}
              {item.name === 'Historial' && (
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              )}
              {item.name === 'DryWall Monitor' && (
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
              )}
              <span className="hidden sm:block">{item.name}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default BankSidebar;
import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { useTheme } from '../../contexts/ThemeContext';
import ThemeSwitcher from '../ThemeSwitcher';
import { FEATURES, APP_VERSION } from '../../config';

const Layout: React.FC = () => {
  const { authState, logout } = useAuth();
  const { isConnected } = useWebSocket();
  const navigate = useNavigate();
  const location = useLocation();

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const { isDark } = useTheme();

  return (
    <div className={`min-h-screen ${isDark ? 'dark bg-dark-800' : 'bg-gray-100'}`}>
      {/* Navigation */}
      <nav className="bg-indigo-600 dark:bg-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Link to="/" className="text-white font-bold text-xl">
                  Workflow Builder
                </Link>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <Link
                    to="/"
                    className={`px-3 py-2 rounded-md text-sm font-medium ${
                      isActive('/') && !isActive('/workflows') && !isActive('/schedules')
                        ? 'bg-indigo-700 text-white'
                        : 'text-indigo-200 hover:bg-indigo-500 hover:text-white'
                    }`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/workflows"
                    className={`px-3 py-2 rounded-md text-sm font-medium ${
                      isActive('/workflows')
                        ? 'bg-indigo-700 text-white'
                        : 'text-indigo-200 hover:bg-indigo-500 hover:text-white'
                    }`}
                  >
                    Workflows
                  </Link>
                  {FEATURES.ENABLE_SCHEDULING && (
                    <Link
                      to="/schedules"
                      className={`px-3 py-2 rounded-md text-sm font-medium ${
                        isActive('/schedules')
                          ? 'bg-indigo-700 text-white'
                          : 'text-indigo-200 hover:bg-indigo-500 hover:text-white'
                      }`}
                    >
                      Schedules
                    </Link>
                  )}
                </div>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="ml-4 flex items-center md:ml-6">
                {/* WebSocket status indicator */}
                {FEATURES.WEBSOCKETS_ENABLED && (
                  <div className="mr-4 flex items-center">
                    <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                    <span className="ml-2 text-xs text-indigo-200">
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                )}

                {/* Profile dropdown */}
                <div className="ml-3 relative">
                  <div>
                    <button
                      type="button"
                      className="max-w-xs bg-indigo-600 rounded-full flex items-center text-sm text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-indigo-600 focus:ring-white"
                      id="user-menu-button"
                      onClick={() => navigate('/profile')}
                    >
                      <span className="sr-only">Open user menu</span>
                      <div className="h-8 w-8 rounded-full bg-indigo-700 flex items-center justify-center">
                        <span className="text-sm font-medium text-white">
                          {authState.user?.username?.charAt(0).toUpperCase() || 'U'}
                        </span>
                      </div>
                    </button>
                  </div>
                </div>

                {/* Theme switcher */}
                <ThemeSwitcher className="ml-3" />

                {/* Logout button */}
                <button
                  type="button"
                  onClick={handleLogout}
                  className="ml-3 px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-200 hover:bg-indigo-500 hover:text-white"
                >
                  Logout
                </button>
              </div>
            </div>
            <div className="-mr-2 flex md:hidden">
              {/* Mobile menu button */}
              <button
                type="button"
                className="bg-indigo-600 inline-flex items-center justify-center p-2 rounded-md text-indigo-200 hover:text-white hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-indigo-600 focus:ring-white"
                aria-controls="mobile-menu"
                aria-expanded="false"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                <span className="sr-only">Open main menu</span>
                {/* Icon when menu is closed */}
                <svg
                  className={`${isMobileMenuOpen ? 'hidden' : 'block'} h-6 w-6`}
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                {/* Icon when menu is open */}
                <svg
                  className={`${isMobileMenuOpen ? 'block' : 'hidden'} h-6 w-6`}
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <div
          className={`${isMobileMenuOpen ? 'block' : 'hidden'} md:hidden`}
          id="mobile-menu"
        >
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link
              to="/"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/') && !isActive('/workflows') && !isActive('/schedules')
                  ? 'bg-indigo-700 text-white'
                  : 'text-indigo-200 hover:bg-indigo-500 hover:text-white'
              }`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              to="/workflows"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/workflows')
                  ? 'bg-indigo-700 text-white'
                  : 'text-indigo-200 hover:bg-indigo-500 hover:text-white'
              }`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Workflows
            </Link>
            {FEATURES.ENABLE_SCHEDULING && (
              <Link
                to="/schedules"
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive('/schedules')
                    ? 'bg-indigo-700 text-white'
                    : 'text-indigo-200 hover:bg-indigo-500 hover:text-white'
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Schedules
              </Link>
            )}
          </div>
          <div className="pt-4 pb-3 border-t border-indigo-700">
            <div className="flex items-center px-5">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-indigo-700 flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {authState.user?.username?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <div className="text-base font-medium text-white">{authState.user?.username}</div>
                <div className="text-sm font-medium text-indigo-300">{authState.user?.email}</div>
              </div>
            </div>
            <div className="mt-3 px-2 space-y-1">
              <Link
                to="/profile"
                className="block px-3 py-2 rounded-md text-base font-medium text-indigo-200 hover:bg-indigo-500 hover:text-white"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Your Profile
              </Link>
              <button
                type="button"
                onClick={() => {
                  handleLogout();
                  setIsMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-indigo-200 hover:bg-indigo-500 hover:text-white"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-dark-900 dark:text-gray-300">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              &copy; {new Date().getFullYear()} Workflow Builder
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Version {APP_VERSION}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;

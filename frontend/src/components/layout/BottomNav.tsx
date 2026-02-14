import { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { NotificationsPanel } from '../notifications/NotificationsPanel';
import { recommendationsService } from '../../services/recommendations';
import {
  HomeIcon,
  CreditCardIcon,
  ChartBarIcon,
  FlagIcon,
  ExclamationTriangleIcon,
  BellIcon,
  ArrowRightOnRectangleIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  CreditCardIcon as CreditCardIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  FlagIcon as FlagIconSolid,
  ExclamationTriangleIcon as ExclamationTriangleIconSolid,
} from '@heroicons/react/24/solid';
import { useAuthStore } from '../../store/authStore';

const navigation = [
  { name: 'Overview', href: '/', icon: HomeIcon, iconSolid: HomeIconSolid },
  { name: 'Transactions', href: '/transactions', icon: CreditCardIcon, iconSolid: CreditCardIconSolid },
  { name: 'Budgets', href: '/budgets', icon: ChartBarIcon, iconSolid: ChartBarIconSolid },
  { name: 'Goals', href: '/goals', icon: FlagIcon, iconSolid: FlagIconSolid },
  { name: 'Anomalies', href: '/anomalies', icon: ExclamationTriangleIcon, iconSolid: ExclamationTriangleIconSolid },
];

export function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const profileRef = useRef<HTMLDivElement>(null);

  // Load notification count function
  const loadNotificationCount = async () => {
    try {
      const data = await recommendationsService.getAll();
      setNotificationCount(data.recommendations.length);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  // Load notifications on mount and set interval
  useEffect(() => {
    loadNotificationCount();
    
    // Refresh every 5 minutes
    const interval = setInterval(loadNotificationCount, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Close profile menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setShowProfileMenu(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Desktop & Tablet - Ultra smooth floating bar */}
      <nav className="hidden sm:block fixed bottom-4 left-1/2 -translate-x-1/2 z-50 w-[46%] max-w-5xl">
        <div className="bg-white/20 backdrop-blur-3xl border border-white/30 rounded-full shadow-[0_8px_32px_0_rgba(0,0,0,0.12)] px-3 py-2 transition-all duration-500 hover:shadow-[0_12px_48px_0_rgba(0,0,0,0.15)]">
          <div className="flex items-center justify-center space-x-1">
            {/* Navigation items */}
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              const Icon = isActive ? item.iconSolid : item.icon;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    relative group flex items-center justify-center gap-2 px-5 py-2.5 rounded-full 
                    transition-all duration-300 ease-out
                    transform-gpu
                    ${isActive 
                      ? 'bg-primary-500/90 text-white shadow-lg shadow-primary-500/40 scale-105' 
                      : 'text-gray-800 hover:bg-white/50 hover:scale-105 hover:shadow-md active:scale-95'
                    }
                  `}
                  title={item.name}
                >
                  <Icon className={`h-5 w-5 transition-all duration-300 ${isActive ? '' : 'group-hover:scale-110'}`} />
                  <span className={`
                    text-sm font-medium 
                    transition-all duration-300 ease-out
                    ${isActive 
                      ? 'inline opacity-100 max-w-32' 
                      : 'max-w-0 opacity-0 group-hover:max-w-32 group-hover:opacity-100 group-hover:ml-1 overflow-hidden'
                    }
                  `}>
                    {item.name}
                  </span>
                  
                  {/* Ripple effect on click */}
                  <span className="absolute inset-0 rounded-full bg-white/20 scale-0 group-active:scale-100 transition-transform duration-300 ease-out" />
                </Link>
              );
            })}

            {/* Divider with gradient fade */}
            <div className="relative h-8 w-px mx-2 overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/40 to-transparent animate-pulse" />
            </div>

            {/* Notifications */}
            <button
              onClick={() => setShowNotifications(true)}
              className="relative flex items-center justify-center gap-2 px-4 py-2.5 rounded-full 
                        text-gray-800 hover:bg-white/50 hover:scale-105 active:scale-95
                        transition-all duration-300 ease-out group transform-gpu"
              title="Notifications"
            >
              <BellIcon className={`h-5 w-5 transition-all duration-300 group-hover:scale-110 ${notificationCount > 0 ? 'animate-wiggle' : ''}`} />
              {notificationCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center h-5 w-5 text-xs font-bold text-white bg-gradient-to-br from-red-500 to-red-600 rounded-full ring-2 ring-white/60 shadow-lg animate-bounce-slow">
                  {notificationCount}
                </span>
              )}
              <span className={`
                text-sm font-medium 
                transition-all duration-300 ease-out
                max-w-0 opacity-0 group-hover:max-w-32 group-hover:opacity-100 group-hover:ml-1 overflow-hidden
              `}>
                Alerts
              </span>
            </button>

            {/* User Profile with smooth dropdown */}
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-full 
                          text-gray-800 hover:bg-white/50 hover:scale-105 active:scale-95
                          transition-all duration-300 ease-out group transform-gpu"
                title={user?.full_name || 'Profile'}
              >
                <div className={`
                  h-7 w-7 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 
                  flex items-center justify-center text-white font-bold text-sm 
                  ring-2 ring-white/60 shadow-lg
                  transition-all duration-300 group-hover:scale-110 group-hover:ring-4
                  ${showProfileMenu ? 'scale-110 ring-4' : ''}
                `}>
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <span className={`
                  text-sm font-medium 
                  transition-all duration-300 ease-out
                  max-w-0 opacity-0 group-hover:max-w-32 group-hover:opacity-100 group-hover:ml-1 overflow-hidden
                `}>
                  Profile
                </span>
              </button>

              {/* Profile dropdown with smooth slide & fade */}
              <div className={`
                absolute bottom-full mb-4 right-0 w-72 
                bg-white/90 backdrop-blur-3xl rounded-2xl 
                shadow-[0_8px_32px_0_rgba(0,0,0,0.18)] border border-white/30 
                overflow-hidden
                transition-all duration-300 ease-out origin-bottom-right
                ${showProfileMenu 
                  ? 'opacity-100 scale-100 translate-y-0' 
                  : 'opacity-0 scale-95 translate-y-4 pointer-events-none'
                }
              `}>
                {/* User info */}
                <div className="bg-gradient-to-br from-primary-500 to-primary-600 p-5 text-white relative overflow-hidden">
                  {/* Animated background gradient */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary-400/20 to-transparent animate-pulse" />
                  
                  <div className="flex items-center space-x-3 relative z-10">
                    <div className="h-14 w-14 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white font-bold text-xl ring-2 ring-white/30 transition-transform duration-300 hover:scale-110">
                      {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-lg truncate transition-all duration-300 hover:text-primary-100">
                        {user?.full_name || 'User'}
                      </p>
                      <p className="text-sm text-primary-100 truncate">
                        {user?.email}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Menu items with stagger animation */}
                <div className="p-2">
                  <button
                    onClick={() => {
                      setShowProfileMenu(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl 
                              hover:bg-gray-100/80 active:scale-98
                              transition-all duration-200 ease-out text-left group transform-gpu"
                  >
                    <UserCircleIcon className="h-5 w-5 text-gray-400 transition-all duration-200 group-hover:text-primary-500 group-hover:scale-110" />
                    <span className="text-sm font-medium text-gray-700 transition-colors duration-200 group-hover:text-gray-900">
                      View Profile
                    </span>
                  </button>

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl 
                              hover:bg-red-50/80 active:scale-98
                              transition-all duration-200 ease-out text-left group transform-gpu"
                  >
                    <ArrowRightOnRectangleIcon className="h-5 w-5 text-red-400 transition-all duration-200 group-hover:text-red-600 group-hover:scale-110" />
                    <span className="text-sm font-medium text-red-600 transition-colors duration-200 group-hover:text-red-700">
                      Logout
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile - Fixed bottom bar */}
      <nav className="sm:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-xl border-t border-gray-200/50 safe-area-bottom transition-all duration-300">
        <div className="flex items-center justify-around px-2 py-2">
          {/* Navigation items */}
          {navigation.map((item, index) => {
            const isActive = location.pathname === item.href;
            const Icon = isActive ? item.iconSolid : item.icon;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex flex-col items-center justify-center flex-1 py-2 px-1 rounded-xl
                  transition-all duration-300 ease-out transform-gpu
                  ${isActive 
                    ? 'text-primary-600 scale-105' 
                    : 'text-gray-500 active:scale-95'
                  }
                `}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <Icon className={`h-6 w-6 transition-all duration-300 ${isActive ? 'scale-110' : 'hover:scale-110'}`} />
                <span className={`text-xs mt-1 font-medium transition-all duration-300 ${isActive ? 'opacity-100' : 'opacity-70'}`}>
                  {item.name === 'Transactions' ? 'Txns' : item.name.split(' ')[0]}
                </span>
              </Link>
            );
          })}

          {/* Notifications */}
          <button
            onClick={() => setShowNotifications(true)}
            className="relative flex flex-col items-center justify-center flex-1 py-2 px-1 rounded-xl text-gray-500 active:scale-95 transition-all duration-300 transform-gpu"
          >
            <BellIcon className={`h-6 w-6 transition-transform duration-300 ${notificationCount > 0 ? 'animate-wiggle' : ''}`} />
            {notificationCount > 0 && (
              <span className="absolute top-1 right-2 flex items-center justify-center h-4 w-4 text-xs font-bold text-white bg-red-500 rounded-full animate-bounce-slow">
                {notificationCount}
              </span>
            )}
            <span className="text-xs mt-1 font-medium opacity-70">Alerts</span>
          </button>

          {/* User Profile */}
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className={`
              flex flex-col items-center justify-center flex-1 py-2 px-1 rounded-xl text-gray-500 
              active:scale-95 transition-all duration-300 transform-gpu
              ${showProfileMenu ? 'text-primary-600 scale-105' : ''}
            `}
          >
            <div className={`
              h-6 w-6 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 
              flex items-center justify-center text-white font-bold text-xs
              transition-all duration-300
              ${showProfileMenu ? 'scale-110 ring-2 ring-primary-300' : ''}
            `}>
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className={`text-xs mt-1 font-medium transition-all duration-300 ${showProfileMenu ? 'opacity-100' : 'opacity-70'}`}>
              Profile
            </span>
          </button>
        </div>

        {/* Mobile profile menu with slide animation */}
        <div className={`
          absolute bottom-full left-0 right-0 bg-white/95 backdrop-blur-xl border-t border-gray-200/50 shadow-xl
          transition-all duration-300 ease-out
          ${showProfileMenu 
            ? 'opacity-100 translate-y-0' 
            : 'opacity-0 translate-y-4 pointer-events-none'
          }
        `}>
          <div className="p-4">
            <div className="flex items-center space-x-3 mb-4 pb-4 border-b border-gray-200">
              <div className="h-12 w-12 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white font-bold text-lg">
                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 truncate">{user?.full_name || 'User'}</p>
                <p className="text-sm text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>

            <button
              onClick={() => setShowProfileMenu(false)}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-gray-100/80 transition-colors text-left mb-2"
            >
              <UserCircleIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">View Profile</span>
            </button>

            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl bg-red-50/80 hover:bg-red-100 transition-colors text-left"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5 text-red-500" />
              <span className="text-sm font-medium text-red-600">Logout</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Notifications Panel - Outside of navigation */}
      <NotificationsPanel
        isOpen={showNotifications}
        onClose={() => {
          setShowNotifications(false);
          loadNotificationCount(); // Refresh count when closing
        }}
      />
    </>
  );
}

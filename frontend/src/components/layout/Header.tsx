import { BellIcon, Cog6ToothIcon, Bars3Icon } from '@heroicons/react/24/outline';

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <div className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6">
      <div className="flex items-center space-x-4">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
        >
          <Bars3Icon className="h-6 w-6 text-gray-600" />
        </button>

        <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
          Dashboard
        </h2>
      </div>

      <div className="flex items-center space-x-2 sm:space-x-4">
        {/* Notifications */}
        <button className="relative p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
          <BellIcon className="h-5 w-5 sm:h-6 sm:w-6" />
          <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
        </button>

        {/* Settings */}
        <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
          <Cog6ToothIcon className="h-5 w-5 sm:h-6 sm:w-6" />
        </button>
      </div>
    </div>
  );
}

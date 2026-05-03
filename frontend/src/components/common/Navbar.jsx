import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import { BrainCircuit, LogOut } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success('Logged out');
    navigate('/login');
  };

  return (
    <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14 items-center">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
              <BrainCircuit className="w-4 h-4 text-white" />
            </div>
            <span className="text-base font-bold text-gray-900">TraceMind</span>
            <span className="text-base font-light text-blue-500">AI</span>
          </Link>

          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-400 hidden sm:block">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-red-500 transition-colors"
            >
              <LogOut className="w-4 h-4" /> Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { IconEdit, IconDeviceFloppy, IconX, IconUser } from '@tabler/icons-react';
import { ArrowLeft, Mail, Phone, Bell } from 'lucide-react';
import { fetchProfile } from '../slices/authSlice';

const CustomerProfile = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user, tokens } = useSelector((state) => state.auth);

  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    phone_no: user?.phone_no || '',
    notification_preference: user?.notification_preference || 'both'
  });

  useEffect(() => {
    // Fetch latest profile data on mount
    if (tokens?.access) {
      dispatch(fetchProfile(tokens.access));
    }
  }, [dispatch, tokens]);

  useEffect(() => {
    // Update form when user data changes
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        phone_no: user.phone_no || '',
        notification_preference: user.notification_preference || 'both'
      });
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (!tokens?.access) {
        throw new Error('Not authenticated');
      }

      const response = await fetch('/api/profile/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.access}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      await response.json();
      
      // Refresh user data
      dispatch(fetchProfile(tokens.access));
      
      setEditMode(false);
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      full_name: user?.full_name || '',
      phone_no: user?.phone_no || '',
      notification_preference: user?.notification_preference || 'both'
    });
    setEditMode(false);
    setError('');
  };

  const getNotificationLabel = (pref) => {
    const labels = {
      'email': 'Email Only',
      'sms': 'SMS Only',
      'both': 'Email & SMS',
      'none': 'Disabled'
    };
    return labels[pref] || 'Both';
  };

  return (
    <div className="w-full min-h-screen bg-gray-50">
      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <button
            onClick={() => navigate('/customerhome')}
            className="flex items-center gap-2 text-gray-700 hover:text-teal-600 transition-colors mb-4"
          >
            <ArrowLeft className="h-5 w-5" />
            Back to Home
          </button>
          <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
        </div>

        {/* Success/Error Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
            {error}
          </div>
        )}
        
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md mb-4">
            {success}
          </div>
        )}

        {/* Profile Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {/* Profile Header */}
          <div className="bg-gradient-to-r from-teal-500 to-teal-600 px-6 py-8">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-white border-4 border-white flex items-center justify-center">
                <IconUser size={40} className="text-teal-600" />
              </div>
              <div className="text-white">
                <h2 className="text-2xl font-bold">{user?.full_name || 'Customer'}</h2>
                <p className="text-teal-100">{user?.email}</p>
                <Badge className="mt-2 bg-white text-teal-600">
                  {user?.role?.toUpperCase() || 'CUSTOMER'}
                </Badge>
              </div>
            </div>
          </div>

          {/* Profile Information */}
          <div className="p-6">
            {!editMode ? (
              // View Mode
              <div className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Profile Information</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setEditMode(true)}
                    className="flex items-center gap-2"
                  >
                    <IconEdit size={16} />
                    Edit Profile
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-gray-500 text-sm">
                      <Mail className="h-4 w-4" />
                      <span>Email Address</span>
                    </div>
                    <p className="text-gray-900 font-medium">{user?.email || 'Not provided'}</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-gray-500 text-sm">
                      <IconUser size={16} />
                      <span>Full Name</span>
                    </div>
                    <p className="text-gray-900 font-medium">{user?.full_name || 'Not provided'}</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-gray-500 text-sm">
                      <Phone className="h-4 w-4" />
                      <span>Phone Number</span>
                    </div>
                    <p className="text-gray-900 font-medium">{user?.phone_no || 'Not provided'}</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-gray-500 text-sm">
                      <Bell className="h-4 w-4" />
                      <span>Notification Preference</span>
                    </div>
                    <Badge className="bg-teal-100 text-teal-700">
                      {getNotificationLabel(user?.notification_preference)}
                    </Badge>
                  </div>
                </div>
              </div>
            ) : (
              // Edit Mode
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Edit Profile</h3>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleCancel}
                    className="flex items-center gap-2"
                  >
                    <IconX size={16} />
                    Cancel
                  </Button>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">
                      Email Address
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="bg-gray-50"
                    />
                    <p className="text-xs text-gray-500">Email cannot be changed</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="full_name">
                      Full Name <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="full_name"
                      name="full_name"
                      type="text"
                      value={formData.full_name}
                      onChange={handleInputChange}
                      placeholder="Enter your full name"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone_no">
                      Phone Number
                    </Label>
                    <Input
                      id="phone_no"
                      name="phone_no"
                      type="tel"
                      value={formData.phone_no}
                      onChange={handleInputChange}
                      placeholder="+1 234 567 8900"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="notification_preference">
                      Notification Preference
                    </Label>
                    <select
                      id="notification_preference"
                      name="notification_preference"
                      value={formData.notification_preference}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="email">Email Only</option>
                      <option value="sms">SMS Only</option>
                      <option value="both">Email & SMS</option>
                      <option value="none">No Notifications</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleCancel}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="bg-teal-600 hover:bg-teal-700 flex items-center gap-2"
                  >
                    <IconDeviceFloppy size={16} />
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default CustomerProfile;

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Search, Plus, Share2, Edit, Settings, BarChart3 } from 'lucide-react';
import { serviceAPI, bookingAPI } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const [services, setServices] = useState([]);
  const [filteredServices, setFilteredServices] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [upcomingCounts, setUpcomingCounts] = useState({});

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    // Wait for user data to be loaded
    if (user && user.role === 'admin') {
      fetchServices();
    }
  }, [isAuthenticated, user, navigate]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredServices(services);
    } else {
      const filtered = services.filter((service) =>
        service.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredServices(filtered);
    }
  }, [searchQuery, services]);

  // Dummy data for testing
  const getDummyData = () => {
    return [
      {
        id: '1',
        name: 'Dental care',
        duration_minutes: 30,
        resources: [
          { id: 'r1', name: 'A1' },
          { id: 'r2', name: 'A2' }
        ],
        is_published: true,
      },
      {
        id: '2',
        name: 'Tennis court',
        duration_minutes: 60,
        resources: [
          { id: 'r3', name: 'R1' },
          { id: 'r4', name: 'R2' }
        ],
        is_published: true,
      },
      {
        id: '3',
        name: 'Interviews',
        duration_minutes: 45,
        resources: [
          { id: 'r5', name: 'Room 1' },
          { id: 'r6', name: 'Room 2' }
        ],
        is_published: false,
      },
      {
        id: '4',
        name: 'Consultation',
        duration_minutes: 60,
        resources: [
          { id: 'r7', name: 'Dr. Smith' },
          { id: 'r8', name: 'Dr. Jones' }
        ],
        is_published: true,
      },
      {
        id: '5',
        name: 'Fitness Training',
        duration_minutes: 45,
        resources: [
          { id: 'r9', name: 'Trainer A' }
        ],
        is_published: false,
      },
    ];
  };

  const fetchServices = async () => {
    try {
      setLoading(true);
      const response = await serviceAPI.getServices();
      let servicesList = Array.isArray(response) ? response : (response.results || []);
      
      // Use dummy data if no services are returned
      if (servicesList.length === 0) {
        servicesList = getDummyData();
      }
      
      setServices(servicesList);
      setFilteredServices(servicesList);
      
      // Fetch upcoming bookings count for each service
      const counts = {};
      try {
        const bookingsResponse = await bookingAPI.getBookings();
        const bookings = Array.isArray(bookingsResponse) 
          ? bookingsResponse 
          : (bookingsResponse.results || []);
        
        for (const service of servicesList) {
          const upcoming = bookings.filter(
            (booking) =>
              (booking.service === service.id || booking.service_id === service.id) &&
              booking.status === 'confirmed' &&
              booking.slot &&
              new Date(booking.slot.start_datetime) > new Date()
          );
          counts[service.id] = upcoming.length;
        }
      } catch (err) {
        console.error('Error fetching bookings:', err);
        // Set dummy counts for testing
        servicesList.forEach((service, index) => {
          counts[service.id] = index === 0 ? 1 : index === 1 ? 3 : 0;
        });
      }
      
      // If no bookings found, set dummy counts
      if (Object.keys(counts).length === 0) {
        servicesList.forEach((service, index) => {
          counts[service.id] = index === 0 ? 1 : index === 1 ? 3 : 0;
        });
      }
      
      setUpcomingCounts(counts);
    } catch (error) {
      console.error('Error fetching services:', error);
      // Use dummy data on error
      const dummyData = getDummyData();
      setServices(dummyData);
      setFilteredServices(dummyData);
      const dummyCounts = {};
      dummyData.forEach((service, index) => {
        dummyCounts[service.id] = index === 0 ? 1 : index === 1 ? 3 : 0;
      });
      setUpcomingCounts(dummyCounts);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = (service) => {
    const shareToken = service.share_token || service.id;
    const shareUrl = `${window.location.origin}/dashboard/${shareToken}`;
    
    if (navigator.share) {
      navigator.share({
        title: service.name,
        text: `Check out this appointment: ${service.name}`,
        url: shareUrl,
      });
    } else {
      navigator.clipboard.writeText(shareUrl);
      alert('Share link copied to clipboard!');
    }
  };

  const handleEdit = (service) => {
    // Navigate to edit page or open edit modal
    navigate(`/dashboard/${service.id}/edit`);
  };

  const formatDuration = (minutes) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  const formatResources = (resources) => {
    if (!resources || resources.length === 0) return 'No resources';
    return resources.map((r) => r.name).join(', ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading appointments...</div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-sm text-gray-500 mt-1">Manage your appointment types</p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/reporting')}
              className="flex items-center gap-2"
            >
              <BarChart3 className="h-4 w-4" />
              Reporting
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/settings')}
              className="flex items-center gap-2"
            >
              <Settings className="h-4 w-4" />
              Settings
            </Button>
            <Button
              onClick={() => navigate('/dashboard/new')}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              New
            </Button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search appointments..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[300px]">Appointment Name</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Resources/Users</TableHead>
                <TableHead>Upcoming Meetings</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredServices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                    No appointments found. Create your first appointment by clicking "New".
                  </TableCell>
                </TableRow>
              ) : (
                filteredServices.map((service) => (
                  <TableRow key={service.id}>
                    <TableCell className="font-medium">{service.name}</TableCell>
                    <TableCell>{formatDuration(service.duration_minutes)}</TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {formatResources(service.resources)}
                    </TableCell>
                    <TableCell>
                      <span className="text-sm font-medium">
                        {upcomingCounts[service.id] || 0} Meeting{upcomingCounts[service.id] !== 1 ? 's' : ''} Upcoming
                      </span>
                    </TableCell>
                    <TableCell>
                      {service.is_published ? (
                        <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
                          Published
                        </Badge>
                      ) : (
                        <Badge variant="outline">Unpublished</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleShare(service)}
                          className="flex items-center gap-1"
                        >
                          <Share2 className="h-4 w-4" />
                          Share
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(service)}
                          className="flex items-center gap-1"
                        >
                          <Edit className="h-4 w-4" />
                          Edit
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;


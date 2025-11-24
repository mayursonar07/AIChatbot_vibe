import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Loader, CheckCircle, AlertCircle } from 'lucide-react';
import '../App.css';

interface RegistrationFormData {
  partnerType: string;
  technicalContactName: string;
  technicalContactPhone: string;
  technicalContactEmail: string;
  transmissionPreference: string;
  onBehalfOfAnotherParty: string;
  companyName: string;
  companyAddress: string;
  businessContactName: string;
  businessContactPhone: string;
  businessContactEmail: string;
}

function Registration() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  
  const [formData, setFormData] = useState<RegistrationFormData>({
    partnerType: 'External',
    technicalContactName: '',
    technicalContactPhone: '',
    technicalContactEmail: '',
    transmissionPreference: '',
    onBehalfOfAnotherParty: '',
    companyName: '',
    companyAddress: '',
    businessContactName: '',
    businessContactPhone: '',
    businessContactEmail: '',
  });

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    const requiredFields: (keyof RegistrationFormData)[] = [
      'technicalContactName',
      'technicalContactPhone',
      'technicalContactEmail',
      'companyName',
      'companyAddress',
      'businessContactName',
      'businessContactPhone',
      'businessContactEmail',
    ];

    for (const field of requiredFields) {
      if (!formData[field]) {
        showNotification('error', `Please fill in all required fields`);
        return;
      }
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.technicalContactEmail) || !emailRegex.test(formData.businessContactEmail)) {
      showNotification('error', 'Please enter valid email addresses');
      return;
    }

    setLoading(true);

    try {
      // TODO: Replace with actual API endpoint when provided
      await axios.post('/api/registration', formData);
      
      showNotification('success', 'Registration submitted successfully!');
      
      // Reset form after successful submission
      setTimeout(() => {
        navigate('/');
      }, 2000);
      
    } catch (error: any) {
      console.error('Registration error:', error);
      showNotification('error', error.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
          <span>{notification.message}</span>
        </div>
      )}

      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>GFTS Registration</h1>
          </div>
          <div className="header-actions">
            <button className="btn btn-secondary" onClick={() => navigate('/')}>
              Back to Home
            </button>
          </div>
        </div>
      </header>

      <div className="main-content">
        <main className="chat-container">
          <div className="transfer-form-container">
            <div className="transfer-form-header">
              <h2>New Transmission Registration</h2>
              <p>Please provide the following details to set up a new file transmission.</p>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="registration-form-grid">
                {/* Left Column - Technical Contact */}
                <div className="form-column">
                  <div className="form-group">
                    <label htmlFor="partnerType">
                      <span className="required">*</span> Are you transmitting with an Internal or External Partner?
                    </label>
                    <select
                      id="partnerType"
                      name="partnerType"
                      value={formData.partnerType}
                      onChange={handleInputChange}
                      className="form-select"
                      required
                    >
                      <option value="Internal">Internal</option>
                      <option value="External">External</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="technicalContactName">
                      <span className="required">*</span> Technical Contact Name
                    </label>
                    <input
                      type="text"
                      id="technicalContactName"
                      name="technicalContactName"
                      value={formData.technicalContactName}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="technicalContactPhone">
                      <span className="required">*</span> Technical Contact Phone
                    </label>
                    <input
                      type="tel"
                      id="technicalContactPhone"
                      name="technicalContactPhone"
                      value={formData.technicalContactPhone}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="technicalContactEmail">
                      <span className="required">*</span> Technical Contact Email
                    </label>
                    <input
                      type="email"
                      id="technicalContactEmail"
                      name="technicalContactEmail"
                      value={formData.technicalContactEmail}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="transmissionPreference">
                      <span className="required">*</span> Do you know the transmission preference?
                    </label>
                    <select
                      id="transmissionPreference"
                      name="transmissionPreference"
                      value={formData.transmissionPreference}
                      onChange={handleInputChange}
                      className="form-select"
                    >
                      <option value="">-- None --</option>
                      <option value="SFTP">SFTP</option>
                      <option value="NDM">NDM</option>
                      <option value="API">API</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="onBehalfOfAnotherParty">
                      <span className="required">*</span> Is this transmission on behalf of another party?
                    </label>
                    <select
                      id="onBehalfOfAnotherParty"
                      name="onBehalfOfAnotherParty"
                      value={formData.onBehalfOfAnotherParty}
                      onChange={handleInputChange}
                      className="form-select"
                    >
                      <option value="">-- None --</option>
                      <option value="Yes">Yes</option>
                      <option value="No">No</option>
                    </select>
                  </div>
                </div>

                {/* Right Column - Company/Business Contact */}
                <div className="form-column">
                  <div className="form-group">
                    <label htmlFor="companyName">
                      <span className="required">*</span> Company name
                    </label>
                    <input
                      type="text"
                      id="companyName"
                      name="companyName"
                      value={formData.companyName}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="companyAddress">
                      <span className="required">*</span> Company Address
                    </label>
                    <textarea
                      id="companyAddress"
                      name="companyAddress"
                      value={formData.companyAddress}
                      onChange={handleInputChange}
                      className="form-textarea"
                      rows={3}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="businessContactName">
                      <span className="required">*</span> Business Contact Name
                    </label>
                    <input
                      type="text"
                      id="businessContactName"
                      name="businessContactName"
                      value={formData.businessContactName}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="businessContactPhone">
                      <span className="required">*</span> Business Contact Phone
                    </label>
                    <input
                      type="tel"
                      id="businessContactPhone"
                      name="businessContactPhone"
                      value={formData.businessContactPhone}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="businessContactEmail">
                      <span className="required">*</span> Business Contact Email
                    </label>
                    <input
                      type="email"
                      id="businessContactEmail"
                      name="businessContactEmail"
                      value={formData.businessContactEmail}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  className="btn btn-primary btn-block btn-transfer"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader size={18} className="spinner" />
                      Submitting...
                    </>
                  ) : (
                    'Submit Registration'
                  )}
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Registration;


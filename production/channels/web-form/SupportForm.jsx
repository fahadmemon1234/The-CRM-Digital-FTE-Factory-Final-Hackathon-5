/**
 * TechCorp Customer Success AI Agent - Web Support Form Component
 * 
 * A React component for customers to submit support requests via web form.
 * 
 * INCUBATION MAPPING:
 * -------------------
 * Incubation: No web form UI (simulated in prototype.py)
 * Production: Full React component with validation and API integration
 * 
 * Features:
 * - Form validation (name, email, subject, message length)
 * - Category and priority selection
 * - Character count for message
 * - Loading state with spinner
 * - Success state with ticket ID
 * - Error handling
 * - Tailwind CSS styling
 * 
 * Usage:
 *   import SupportForm from './web-form/SupportForm';
 *   
 *   <SupportForm 
 *     apiEndpoint="/api/support/submit"
 *     onSuccess={(ticketId) => console.log('Ticket:', ticketId)}
 *   />
 * 
 * Author: AI Engineering Team
 * Version: 1.0.0 (Production)
 */

import React, { useState } from 'react';

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Support categories available for selection.
 * INCUBATION: Hardcoded category list in prototype.py
 * PRODUCTION: Configurable constant array
 */
const CATEGORIES = [
  { value: 'general', label: 'General Question' },
  { value: 'technical', label: 'Technical Support' },
  { value: 'billing', label: 'Billing Inquiry' },
  { value: 'bug_report', label: 'Bug Report' },
  { value: 'feedback', label: 'Feedback' }
];

/**
 * Priority levels for support requests.
 * INCUBATION: Simple string enum in prototype.py
 * PRODUCTION: Configurable constant array with labels
 */
const PRIORITIES = [
  { value: 'low', label: 'Low - Not urgent' },
  { value: 'medium', label: 'Medium - Need help soon' },
  { value: 'high', label: 'High - Urgent issue' }
];

/**
 * Email validation regex pattern.
 * Matches standard email format: local@domain.tld
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Maximum message length in characters.
 */
const MAX_MESSAGE_LENGTH = 1000;

// ============================================================================
// SUPPORT FORM COMPONENT
// ============================================================================

/**
 * SupportForm Component
 * 
 * @param {Object} props - Component props
 * @param {string} props.apiEndpoint - API endpoint for form submission (default: '/api/support/submit')
 * @param {function} props.onSuccess - Callback function when submission succeeds
 * @param {function} props.onError - Callback function when submission fails
 * @param {string} props.className - Additional CSS classes for styling
 */
export default function SupportForm({
  apiEndpoint = '/api/support/submit',
  onSuccess,
  onError,
  className = ''
}) {
  // ==========================================================================
  // STATE
  // ==========================================================================
  
  /**
   * Form data state.
   * INCUBATION: Simple dict in prototype.py
   * PRODUCTION: React state with typed fields
   */
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    category: 'general',
    priority: 'medium',
    message: ''
  });

  /**
   * Submission status state.
   * Values: 'idle' | 'submitting' | 'success' | 'error'
   */
  const [status, setStatus] = useState('idle');

  /**
   * Ticket ID returned on successful submission.
   */
  const [ticketId, setTicketId] = useState(null);

  /**
   * Error message state.
   */
  const [error, setError] = useState(null);

  /**
   * Form validation errors state.
   */
  const [validationErrors, setValidationErrors] = useState({});

  // ==========================================================================
  // EVENT HANDLERS
  // ==========================================================================

  /**
   * Handle input changes and update form data.
   * 
   * INCUBATION: No form handling (simulated)
   * PRODUCTION: React controlled component with state updates
   * 
   * @param {Event} e - Input change event
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear validation error for this field when user types
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  /**
   * Validate form data before submission.
   * 
   * INCUBATION: Simple validation in prototype.py
   * PRODUCTION: Comprehensive validation with error messages
   * 
   * @returns {boolean} True if form is valid
   */
  const validateForm = () => {
    const errors = {};

    // Name validation: at least 2 characters after trim
    if (!formData.name || formData.name.trim().length < 2) {
      errors.name = 'Please enter your name (at least 2 characters)';
    }

    // Email validation: valid email format
    if (!formData.email || !EMAIL_REGEX.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Subject validation: at least 5 characters
    if (!formData.subject || formData.subject.trim().length < 5) {
      errors.subject = 'Please enter a subject (at least 5 characters)';
    }

    // Message validation: at least 10 characters
    if (!formData.message || formData.message.trim().length < 10) {
      errors.message = 'Please enter a message (at least 10 characters)';
    }

    // Message length check
    if (formData.message.length > MAX_MESSAGE_LENGTH) {
      errors.message = `Message is too long (maximum ${MAX_MESSAGE_LENGTH} characters)`;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission.
   * 
   * INCUBATION: Simulated submission in prototype.py
   * PRODUCTION: Real API call with error handling
   * 
   * @param {Event} e - Form submit event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Clear previous errors
    setError(null);

    // Validate form
    if (!validateForm()) {
      return;
    }

    // Set submitting status
    setStatus('submitting');

    try {
      // Submit to API endpoint
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Update state on success
      setTicketId(data.ticket_id);
      setStatus('success');

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(data.ticket_id);
      }

    } catch (err) {
      // Handle error
      const errorMessage = err.message || 'Failed to submit form. Please try again.';
      setError(errorMessage);
      setStatus('error');

      // Call error callback if provided
      if (onError) {
        onError(err);
      }
    }
  };

  /**
   * Reset form to initial state.
   */
  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      subject: '',
      category: 'general',
      priority: 'medium',
      message: ''
    });
    setStatus('idle');
    setTicketId(null);
    setError(null);
    setValidationErrors({});
  };

  // ==========================================================================
  // RENDER HELPERS
  // ==========================================================================

  /**
   * Render success state after successful submission.
   * 
   * INCUBATION: Print statement in prototype.py
   * PRODUCTION: Styled success UI with ticket ID
   */
  const renderSuccessState = () => (
    <div className="text-center py-8">
      {/* Green checkmark icon in circle */}
      <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
        <svg
          className="w-10 h-10 text-green-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>

      {/* Success heading */}
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Thank You!
      </h2>

      {/* Success message */}
      <p className="text-gray-600 mb-6">
        Your support request has been submitted successfully.
      </p>

      {/* Ticket ID display */}
      {ticketId && (
        <div className="bg-gray-100 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-500 mb-1">Ticket ID</p>
          <p className="text-lg font-mono font-semibold text-gray-900">
            {ticketId}
          </p>
        </div>
      )}

      {/* Expected response time */}
      <p className="text-sm text-gray-500 mb-6">
        We typically respond within 5 minutes during business hours.
      </p>

      {/* Submit another button */}
      <button
        type="button"
        onClick={resetForm}
        className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
      >
        Submit Another Request
      </button>
    </div>
  );

  /**
   * Render error state.
   */
  const renderErrorState = () => (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-red-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">
            Submission Failed
          </h3>
          <p className="mt-1 text-sm text-red-700">{error}</p>
        </div>
        <div className="ml-auto pl-3">
          <button
            type="button"
            onClick={() => {
              setError(null);
              setStatus('idle');
            }}
            className="inline-flex text-red-500 hover:text-red-700"
          >
            <span className="sr-only">Dismiss</span>
            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );

  // ==========================================================================
  // MAIN RENDER
  // ==========================================================================

  return (
    <div className={`max-w-2xl mx-auto ${className}`}>
      {/* Success State */}
      {status === 'success' ? (
        renderSuccessState()
      ) : (
        <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6">
          {/* Error State */}
          {status === 'error' && renderErrorState()}

          {/* Form Title */}
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            Contact Support
          </h1>

          {/* Name Field */}
          <div className="mb-4">
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.name
                  ? 'border-red-300'
                  : 'border-gray-300'
              }`}
              placeholder="Your full name"
            />
            {validationErrors.name && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.name}</p>
            )}
          </div>

          {/* Email Field */}
          <div className="mb-4">
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.email
                  ? 'border-red-300'
                  : 'border-gray-300'
              }`}
              placeholder="your.email@example.com"
            />
            {validationErrors.email && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.email}</p>
            )}
          </div>

          {/* Subject Field */}
          <div className="mb-4">
            <label
              htmlFor="subject"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Subject <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="subject"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.subject
                  ? 'border-red-300'
                  : 'border-gray-300'
              }`}
              placeholder="Brief description of your issue"
            />
            {validationErrors.subject && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.subject}</p>
            )}
          </div>

          {/* Category and Priority (side by side) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {/* Category Field */}
            <div>
              <label
                htmlFor="category"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Category
              </label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
              >
                {CATEGORIES.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Priority Field */}
            <div>
              <label
                htmlFor="priority"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
              >
                {PRIORITIES.map(pri => (
                  <option key={pri.value} value={pri.value}>
                    {pri.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Message Field */}
          <div className="mb-6">
            <label
              htmlFor="message"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Message <span className="text-red-500">*</span>
            </label>
            <textarea
              id="message"
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
              rows={6}
              maxLength={MAX_MESSAGE_LENGTH}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y ${
                validationErrors.message
                  ? 'border-red-300'
                  : 'border-gray-300'
              }`}
              placeholder="Please describe your issue in detail..."
            />
            <div className="flex justify-between items-center mt-1">
              {validationErrors.message ? (
                <p className="text-sm text-red-600">{validationErrors.message}</p>
              ) : (
                <span />
              )}
              <p className="text-sm text-gray-500">
                {formData.message.length}/{MAX_MESSAGE_LENGTH} characters
              </p>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={status === 'submitting'}
            className={`w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white ${
              status === 'submitting'
                ? 'bg-blue-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
            } transition-colors`}
          >
            {status === 'submitting' ? (
              <>
                {/* Loading spinner */}
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Submitting...
              </>
            ) : (
              'Submit Request'
            )}
          </button>

          {/* Privacy Policy Link */}
          <p className="mt-4 text-center text-sm text-gray-500">
            By submitting this form, you agree to our{' '}
            <a
              href="/privacy-policy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              Privacy Policy
            </a>{' '}
            and{' '}
            <a
              href="/terms-of-service"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              Terms of Service
            </a>
            .
          </p>
        </form>
      )}
    </div>
  );
}

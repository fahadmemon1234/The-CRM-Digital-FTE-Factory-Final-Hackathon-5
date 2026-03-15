/**
 * TechCorp Customer Success AI Agent - Web Form Module
 * 
 * This module exports the SupportForm React component
 * for embedding in web applications.
 * 
 * Usage:
 *   import SupportForm from './web-form';
 *   
 *   <SupportForm 
 *     apiEndpoint="/api/support/submit"
 *     onSuccess={(ticketId) => console.log('Ticket:', ticketId)}
 *   />
 * 
 * Author: AI Engineering Team
 * Version: 1.0.0 (Production)
 */

export { default as SupportForm } from './SupportForm';
export { default } from './SupportForm';

// Re-export constants for customization
export { CATEGORIES, PRIORITIES } from './SupportForm';

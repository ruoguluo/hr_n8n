// Configuration constants for the HR JD System

// Webhook URLs
const WEBHOOK_CONFIG = {
    JD_UPLOAD_WEBHOOK: 'http://107.182.26.178:5678/webhook/39e31a92-4f74-4380-b480-4c997a6d01aa'
};

// API Endpoints
const API_CONFIG = {
    BASE_URL: window.location.origin,
    ENDPOINTS: {
        POSITION_INFO: '/api/position-info',
        COMPANY_REGISTRATION: '/api/company-registration',
        COMPANIES: '/api/companies',
        JD_DETAIL: '/api/jd-detail',
        JD_DELETE: '/api/jd'
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WEBHOOK_CONFIG, API_CONFIG };
}
# HR N8N Registration System

A simple web-based registration system for company information and job description (JD) upload, designed to integrate with N8N workflows.

## Features

- **Two-Step Registration Process**:
  - Step 1: Company Registration (name, website, contact person, contact number)
  - Step 2: Job Description (JD) Upload (PDF format)

- **Modern UI**:
  - Responsive design that works on desktop and mobile
  - Progress indicator showing current step
  - Beautiful gradient background
  - Clean, professional interface

- **N8N Integration**:
  - Sends company data to N8N webhook for processing
  - Uploads PDF files to N8N for automated processing
  - Displays formatted feedback from N8N workflows

## Project Structure

```
hr_n8n/
├── html/
│   └── registration.html    # Main registration form
├── server.py               # Python web server
└── README.md              # This file
```

## Setup and Usage

### Prerequisites
- Python 3.x
- Web browser

### Running the Application

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd hr_n8n
   ```

2. Start the web server:
   ```bash
   python3 server.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8000/
   ```

### Configuration

Before using the application, update the webhook URLs in `html/registration.html`:

```javascript
// Replace with your N8N webhook URLs
const WEBHOOK_INFO = 'your-n8n-webhook-url-for-company-info';
const WEBHOOK_PDF = 'your-n8n-webhook-url-for-pdf-upload';
```

## How It Works

1. **Company Registration**: User fills in company details and submits the form
2. **N8N Processing**: Data is sent to N8N webhook, which returns a client ID
3. **PDF Upload**: User uploads a job description PDF file
4. **Feedback Display**: N8N processes the PDF and returns formatted feedback

## Technical Details

- **Frontend**: Pure HTML, CSS, and JavaScript (no frameworks)
- **Backend**: Python built-in HTTP server
- **File Upload**: Multipart form data for PDF files
- **Integration**: RESTful API calls to N8N webhooks

## License

MIT License - feel free to use and modify as needed.
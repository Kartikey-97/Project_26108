# StandIQ n8n Integration Plan

## Emailing PDF Reports to Procurement Officers

To make the live demo look amazing, we can add a simple "Email Report to Officer" button that triggers an n8n webhook. 

### 1. The n8n Workflow

You can set up a simple 3-node workflow in n8n:
1. **Webhook Node**: Listens for a POST request.
2. **Markdown to PDF Node** (or API/HTML to PDF): Converts the analysis payload or a direct UI screenshot into a PDF. (Alternatively, the React frontend can generate the PDF and send the base64/binary to the webhook).
3. **Gmail / SMTP Node**: Sends an email with the PDF attached to the Procurement Officer.

### 2. Frontend Button Implementation

We can add a button in `frontend/src/components/layout/TopNavigation.jsx` or on the Dashboard that triggers this webhook.

# send-email-mcp

A FastMCP-based MCP server for sending emails via the Resend API using Streamable HTTP transport with pass-through authentication.

## Overview
This MCP server provides email sending functionality through the Resend API. It uses pass-through authentication, meaning API credentials are provided via HTTP headers rather than stored in the server configuration. This makes it secure and flexible for multi-tenant use cases.

## Prerequisites
- Install uv (https://docs.astral.sh/uv/getting-started/installation/)
- Resend API key (get one at https://resend.com)

## Installation

1. Clone the repository and navigate to the directory:

```bash
cd send-email-mcp
```

2. Install python version & dependencies:

```bash
uv python install
uv sync
```

## Usage

Start the server on port 8000:

```bash
uv run main.py
```

The server will be available at `http://127.0.0.1:8000/mcp` using Streamable HTTP transport.

## Authentication

This server uses **pass-through authentication**. You must provide the following HTTP headers with each request:

- `X-API-KEY`: Your Resend API key

## Features

### `send_email` Tool

The server provides a comprehensive email sending tool with the following parameters:

- **to_emails**: List of recipient email addresses (max 50)
- **subject**: Email subject line
- **html_content**: HTML content of the email
- **text_content**: Plain text version of the email
- **cc_emails**: List of CC recipient email addresses
- **bcc_emails**: List of BCC recipient email addresses
- **reply_to**: Reply-to email address(es) - single or multiple
- **scheduled_at**: Schedule email for later delivery (natural language or ISO 8601)
- **attachments**: File attachments (max 40MB total after Base64 encoding)
- **tags**: Custom tags for tracking and categorization

### `email-template://` Resource

Get pre-formatted property inquiry email templates.

**URI:** `"email-template://property-inquiry/{property_link}"`

Returns JSON with `subject`, `html`, and `text` fields with SENDER_NAME placeholder, ready to use with the send_email tool.

### Example Queries

Through an AI assistant connected to this MCP server, you can ask:

- "Send an inquiry email to agency@example.com about the apartment at 15 Rue de la Paix"
- "Email contact@realestate.fr to request a viewing for the 2-bedroom in Paris 11th"
- "Send a property inquiry to landlord@example.com about the studio apartment"

## Development

### API Integration

The server uses the Resend API for email delivery. To extend functionality, modify the `_send_email_via_resend` function in `main.py`.

### Tech Stack

- **FastMCP**: Modern MCP server framework
- **httpx**: Async HTTP client for API calls
- **Pydantic**: Data validation and email validation

## License

MIT

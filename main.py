"""
Resend Email MCP Server - Email Sending API
"""

import json
import logging
from typing import Optional

import httpx
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from pydantic import Field, EmailStr

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("resend-mcp")

# API Configuration
RESEND_API_BASE_URL = "https://api.resend.com"

# No authentication on the MCP server - relies on pass-through
mcp = FastMCP("Resend Email", stateless_http=True)

logger.info("🔓 MCP Server initialized (pass-through authentication)")


async def _send_email_via_resend(
    api_key: str,
    sender_email: str,
    to_emails: list[str],
    subject: str,
    html_content: Optional[str] = None,
    text_content: Optional[str] = None,
    cc_emails: Optional[list[str]] = None,
    bcc_emails: Optional[list[str]] = None,
    reply_to: Optional[list[str] | str] = None,
    scheduled_at: Optional[str] = None,
    attachments: Optional[list[dict]] = None,
    tags: Optional[list[dict]] = None,
) -> dict:
    """
    Internal function to send email using the Resend API.

    Args:
        api_key: Resend API key
        sender_email: Sender email address
        to_emails: List of recipient email addresses
        subject: Email subject
        html_content: HTML content of the email (optional if text_content provided)
        text_content: Plain text content (optional if html_content provided)
        cc_emails: List of CC recipient email addresses (optional)
        bcc_emails: List of BCC recipient email addresses (optional)
        reply_to: Reply-to email address(es) - string or list of strings (optional)
        scheduled_at: Schedule email for later - natural language or ISO 8601 (optional)
        attachments: List of attachments with content/filename/path (optional)
        tags: List of custom tags with name/value pairs (optional)

    Returns:
        API response as a dictionary with 'id' field
    """
    url = f"{RESEND_API_BASE_URL}/emails"

    payload = {
        "from": sender_email,
        "to": to_emails,
        "subject": subject,
    }

    if html_content:
        payload["html"] = html_content

    if text_content:
        payload["text"] = text_content

    if cc_emails:
        payload["cc"] = cc_emails

    if bcc_emails:
        payload["bcc"] = bcc_emails

    if reply_to:
        payload["reply_to"] = reply_to

    if scheduled_at:
        payload["scheduled_at"] = scheduled_at

    if attachments:
        payload["attachments"] = attachments

    if tags:
        payload["tags"] = tags

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # Log request details
    logger.info("=" * 80)
    logger.info("📧 Resend API Request")
    logger.info(f"URL: {url}")
    logger.info("Payload:")
    logger.info(f"  From: {sender_email}")
    logger.info(f"  To: {', '.join(to_emails)}")
    if cc_emails:
        logger.info(f"  CC: {', '.join(cc_emails)}")
    if bcc_emails:
        logger.info(f"  BCC: {', '.join(bcc_emails)}")
    logger.info(f"  Subject: {subject}")
    if scheduled_at:
        logger.info(f"  Scheduled At: {scheduled_at}")
    if attachments:
        logger.info(f"  Attachments: {len(attachments)} file(s)")
    if tags:
        logger.info(f"  Tags: {len(tags)} tag(s)")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, headers=request_headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            # Log response details
            logger.info("-" * 80)
            logger.info("✅ Resend API Response")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Email ID: {response_data.get('id', 'N/A')}")
            logger.info(
                f"Response Preview: {json.dumps(response_data, indent=2)[:200]}..."
            )
            logger.info("=" * 80)

            return response_data
        except httpx.HTTPStatusError as e:
            # Get the error details from the response
            try:
                error_details = e.response.json()
                error_message = error_details.get("message", "Unknown error")
            except:
                error_message = e.response.text

            logger.error(
                f"❌ Resend API Error ({e.response.status_code}): {error_message}"
            )

            if e.response.status_code in [401, 403]:
                raise ValueError(
                    f"Authentication failed: {error_message}. Please check your API key and sender domain verification."
                )
            raise ValueError(f"Resend API error: {error_message}")


@mcp.resource(
    uri="email-template://{property_reference}",
    description="Get a real estate inquiry email template for contacting agencies about apartments",
    name="Real Estate Inquiry Template",
)
def get_email_template(
    property_reference: str = "the property",
) -> str:
    """
    Get a professional real estate inquiry email template for apartment viewings.

    Args:
        property_reference: Property reference or description (e.g., "Apartment on 15 Rue de la Paix")

    Returns:
        JSON string with 'subject', 'html' and 'text' versions of the email
    """
    import json

    subject = f"Inquiry regarding {property_reference}"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6; 
            color: #2c3e50;
            margin: 0;
            padding: 0;
        }}
        .container {{ 
            max-width: 600px; 
            margin: 20px auto; 
            padding: 0;
        }}
        .content {{ 
            padding: 30px;
            background-color: #ffffff;
        }}
        .greeting {{
            font-size: 16px;
            margin-bottom: 20px;
        }}
        .message {{
            margin: 20px 0;
            font-size: 15px;
        }}
        .signature {{
            margin-top: 30px;
            font-size: 15px;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <div class="greeting">
                Hello,
            </div>
            <div class="message">
                <p>I am writing to express my interest in this property and would like to schedule a viewing at your earliest convenience.</p>
                <p>I look forward to hearing from you soon.</p>
            </div>
            <div class="signature">
                <p>Best regards</p>
            </div>
            <div class="footer">
                <p>Regarding: {property_reference}</p>
            </div>
        </div>
    </div>
</body>
</html>
    """

    text = f"""Hello,

I am writing to express my interest in this property and would like to schedule a viewing at your earliest convenience.

I look forward to hearing from you soon.

Best regards

---
Regarding: {property_reference}"""

    return json.dumps(
        {
            "subject": subject,
            "html": html.strip(),
            "text": text.strip(),
        },
        indent=2,
    )


@mcp.tool(
    title="Send Email",
    description="Send emails using the Resend API with comprehensive features including attachments, scheduling, and tags",
)
async def send_email(
    to_emails: list[EmailStr] = Field(
        description="List of recipient email addresses (max 50)",
    ),
    subject: str = Field(
        description="Email subject line",
    ),
    html_content: Optional[str] = Field(
        default=None,
        description="HTML content of the email (required if text_content not provided)",
    ),
    text_content: Optional[str] = Field(
        default=None,
        description="Plain text version of the email (required if html_content not provided)",
    ),
    cc_emails: Optional[list[EmailStr]] = Field(
        default=None,
        description="List of CC recipient email addresses",
    ),
    bcc_emails: Optional[list[EmailStr]] = Field(
        default=None,
        description="List of BCC recipient email addresses",
    ),
    reply_to: Optional[list[EmailStr] | EmailStr] = Field(
        default=None,
        description="Reply-to email address(es) - single address or list",
    ),
    scheduled_at: Optional[str] = Field(
        default=None,
        description="Schedule email for later delivery - natural language (e.g., 'in 1 min') or ISO 8601 format",
    ),
    attachments: Optional[list[dict]] = Field(
        default=None,
        description="List of attachments (max 40MB total). Each with: content (Base64 string), filename, optional path/content_type/content_id",
    ),
    tags: Optional[list[dict]] = Field(
        default=None,
        description="Custom tags as key/value pairs. Each tag: name (max 256 chars), value (max 256 chars)",
    ),
) -> dict:
    """
    Send emails using the Resend API. Requires X-RESEND-API-KEY and X-SENDER-EMAIL headers with valid credentials.

    Returns a response containing the email ID and status information.

    Example usage:
    - Send HTML email:
      to_emails=["user@example.com"], subject="Hello", html_content="<p>Hello World!</p>"
    - Send with CC and BCC:
      to_emails=["user@example.com"], subject="Meeting", html_content="<p>Meeting details</p>",
      cc_emails=["manager@example.com"], bcc_emails=["archive@example.com"]
    - Schedule email:
      to_emails=["user@example.com"], subject="Reminder", html_content="<p>Don't forget!</p>",
      scheduled_at="in 1 hour"
    """

    # Extract API key and sender email from request headers using get_http_headers()
    headers = get_http_headers()

    # Debug: Log all received headers
    logger.info(f"🔍 Received headers: {dict(headers)}")

    # Try multiple case variations for headers (HTTP headers are case-insensitive)
    api_key = (
        headers.get("x-resend-api-key")
        or headers.get("X-RESEND-API-KEY")
        or headers.get("X-Resend-Api-Key")
    )
    sender_email = (
        headers.get("x-sender-email")
        or headers.get("X-SENDER-EMAIL")
        or headers.get("X-Sender-Email")
    )

    if not api_key:
        logger.error("❌ Missing X-RESEND-API-KEY header")
        logger.error(f"Available headers: {list(headers.keys())}")
        raise ValueError(
            "Missing X-RESEND-API-KEY header. Please provide your Resend API key."
        )

    if not sender_email:
        logger.error("❌ Missing X-SENDER-EMAIL header")
        raise ValueError(
            "Missing X-SENDER-EMAIL header. Please provide sender email address."
        )

    if not html_content and not text_content:
        logger.error("❌ Neither html_content nor text_content provided")
        raise ValueError(
            "At least one of html_content or text_content must be provided."
        )

    logger.info("🔑 Using API key and sender email from request headers")

    return await _send_email_via_resend(
        api_key=api_key,
        sender_email=sender_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        cc_emails=cc_emails,
        bcc_emails=bcc_emails,
        reply_to=reply_to,
        scheduled_at=scheduled_at,
        attachments=attachments,
        tags=tags,
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

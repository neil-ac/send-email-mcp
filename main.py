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
            try:
                error_message = e.response.json().get("message", e.response.text)
            except:
                error_message = e.response.text

            logger.error(
                f"❌ Resend API Error ({e.response.status_code}): {error_message}"
            )
            raise ValueError(f"Email send failed: {error_message}")


@mcp.resource(
    uri="email-template://property-inquiry/{property_link}",
    description="Get email template with subject, html, and text for property inquiries. Replace the placeholders with the actual values.",
    name="Property Inquiry Email Template",
    mime_type="application/json",
)
def get_email_template(
    property_link: str,
) -> str:
    """Returns JSON with subject, html, and text fields for a property inquiry email.

    Args:
        property_reference: The property reference or description to include in the email
        price: The asking price for the property (default: "the listing price")
        sender_name: Name of the person sending the inquiry (default: "A potential buyer")

    Returns:
        JSON string containing subject, html, and text fields for the email
    """
    subject = f"Interested by your property!"

    text = f"""Hello,

We came across your listing for your property and we're really interested!

Here is the link to the property: {property_link}

Would it be possible to schedule a visit?

Looking forward to hearing back from you!

Thanks,
[SENDER_NAME]
"""

    return json.dumps(
        {
            "subject": subject,
            "text": text.strip(),
        },
        indent=2,
    )


@mcp.tool(
    title="Send Email",
    description="Send emails via Resend API. IMPORTANT: Always include BOTH html_content AND text_content to avoid delivery issues.",
)
async def send_email(
    to_emails: list[EmailStr] = Field(
        description="List of recipient email addresses (max 50)",
    ),
    subject: str = Field(
        description="Email subject line",
    ),
    sender_email: str = Field(
        description="Sender email address, must be verified in your Resend account",
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
    Send emails via Resend API. Always provide both html_content AND text_content for best results.
    Returns email ID on success.
    """

    # Extract API key and sender email from request headers using get_http_headers()
    headers = get_http_headers()
    api_key = headers.get("x-api-key")

    if not api_key:
        logger.error("❌ Missing X-RESEND-API-KEY header")
        raise ValueError(
            "Missing X-RESEND-API-KEY header. Please provide your Resend API key."
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

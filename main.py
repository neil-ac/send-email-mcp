"""
Resend Email MCP Server - Simple Email Sending API
"""

import httpx
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

mcp = FastMCP("Resend Email", stateless_http=True)

RESEND_API_URL = "https://api.resend.com/emails"


@mcp.tool()
async def send_email(
    sender_email: str,
    to_emails: list[str],
    subject: str,
    text_content: str | None = None,
    html_content: str | None = None,
) -> dict:
    """
    Send an email via Resend API.

    Args:
        sender_email: Sender email address (must be verified in Resend)
        to_emails: List of recipient email addresses
        subject: Email subject line
        text_content: Plain text content (required if html_content not provided)
        html_content: HTML content (required if text_content not provided)

    Returns:
        API response with email ID on success
    """
    # Get API key from HTTP headers
    headers = get_http_headers()
    print(f"Received headers: {list(headers.keys())}")
    api_key = headers.get("x-api-key")

    if not api_key:
        raise ValueError(f"Missing x-api-key header. Received headers: {list(headers.keys())}")

    if not text_content and not html_content:
        raise ValueError("At least one of text_content or html_content must be provided")

    print(f"Sending email to {to_emails} with subject: {subject}")

    payload = {
        "from": sender_email,
        "to": to_emails,
        "subject": subject,
    }

    if text_content:
        payload["text"] = text_content
    if html_content:
        payload["html"] = html_content

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        result = response.json()
        print(f"Email sent successfully, ID: {result.get('id')}")
        return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

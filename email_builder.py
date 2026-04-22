"""
email_builder.py - HTML email template for R.S Education newsletter
"""

from config import settings


def build_html_email(name: str, content: str, email: str) -> str:
    """
    Build a clean, responsive HTML email with:
    - Personalized greeting
    - AI-generated content
    - CTA button
    - Unsubscribe link
    """
    unsubscribe_url = f"{settings.BASE_URL}/unsubscribe?email={email}"

    # Convert plain-text AI content to HTML paragraphs
    html_content = _text_to_html(content)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Your Weekly Newsletter – R.S Education</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9;padding:30px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:12px;overflow:hidden;
                      box-shadow:0 4px 20px rgba(0,0,0,0.08);max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1a73e8,#0d47a1);padding:36px 40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:700;letter-spacing:0.5px;">
                📚 R.S Education
              </h1>
              <p style="margin:8px 0 0;color:#bbdefb;font-size:13px;">
                Redefining academic excellence through personalized counseling
              </p>
            </td>
          </tr>

          <!-- Weekly Badge -->
          <tr>
            <td style="background:#e8f0fe;padding:10px 40px;text-align:center;">
              <span style="display:inline-block;background:#1a73e8;color:#fff;
                           font-size:11px;font-weight:600;padding:4px 14px;
                           border-radius:20px;letter-spacing:1px;text-transform:uppercase;">
                Weekly Newsletter
              </span>
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="padding:32px 40px 0;">
              <h2 style="margin:0;font-size:22px;color:#1a237e;font-weight:700;">
                Hi {name} 👋
              </h2>
              <p style="margin:10px 0 0;color:#546e7a;font-size:14px;line-height:1.6;">
                Here's your personalized weekly update from <strong>R.S Education</strong>.
                We've curated the best opportunities just for you! 🎯
              </p>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding:20px 40px 0;">
              <hr style="border:none;border-top:1px solid #e8eaf6;margin:0;" />
            </td>
          </tr>

          <!-- AI-Generated Content -->
          <tr>
            <td style="padding:24px 40px;">
              <div style="color:#37474f;font-size:14px;line-height:1.8;">
                {html_content}
              </div>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding:0 40px;">
              <hr style="border:none;border-top:1px solid #e8eaf6;margin:0;" />
            </td>
          </tr>

          <!-- CTA Button -->
          <tr>
            <td style="padding:28px 40px;text-align:center;">
              <p style="margin:0 0 18px;color:#546e7a;font-size:13px;">
                Ready to explore more opportunities tailored just for you?
              </p>
              <a href="{settings.BASE_URL}"
                 style="display:inline-block;background:linear-gradient(135deg,#1a73e8,#1565c0);
                        color:#ffffff;font-size:15px;font-weight:600;
                        padding:14px 36px;border-radius:8px;text-decoration:none;
                        letter-spacing:0.3px;box-shadow:0 4px 12px rgba(26,115,232,0.35);">
                🚀 Explore More Recommendations
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8f9ff;border-top:1px solid #e8eaf6;
                       padding:20px 40px;text-align:center;border-radius:0 0 12px 12px;">
              <p style="margin:0;color:#90a4ae;font-size:11px;line-height:1.7;">
                You are receiving this email because you subscribed to <strong>R.S Education</strong> newsletter.<br/>
                <a href="{unsubscribe_url}"
                   style="color:#1a73e8;text-decoration:none;font-weight:500;">
                  Unsubscribe anytime
                </a>
                &nbsp;·&nbsp;
                <span>R.S Education, India</span>
              </p>
              <p style="margin:10px 0 0;color:#b0bec5;font-size:10px;">
                © 2025 R.S Education. All rights reserved.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""


def _text_to_html(text: str) -> str:
    """
    Convert plain text with emoji section headers into styled HTML.
    Handles sections like '🎓 TOP COLLEGES:', bullet points, etc.
    """
    lines = text.strip().split("\n")
    html_parts = []
    in_section = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_section:
                html_parts.append("</ul>")
                in_section = False
            continue

        # Section headers (lines with emoji + caps)
        if any(line.startswith(emoji) for emoji in ["🎓", "💰", "📈", "💬"]):
            if in_section:
                html_parts.append("</ul>")
                in_section = False
            html_parts.append(
                f'<p style="margin:16px 0 6px;font-weight:700;'
                f'color:#1a237e;font-size:14px;">{line}</p>'
            )
        # Bullet points
        elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
            if not in_section:
                html_parts.append(
                    '<ul style="margin:4px 0 8px;padding-left:18px;'
                    'color:#37474f;font-size:13px;">'
                )
                in_section = True
            clean = line.lstrip("•-* ").strip()
            html_parts.append(f'<li style="margin-bottom:4px;">{clean}</li>')
        else:
            if in_section:
                html_parts.append("</ul>")
                in_section = False
            html_parts.append(
                f'<p style="margin:0 0 10px;font-size:13px;color:#546e7a;">{line}</p>'
            )

    if in_section:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def get_email_subject(name: str) -> str:
    return f"📚 {name}, your weekly update from R.S Education is here!"

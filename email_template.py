def render_email(
    question: str, tip: str, theme: str, child_name: str, date_str: str, theme_emoji: str = "✨"
) -> str:
    """
    Render an engaging HTML email with navy/gold theme matching the landing page.
    Dark navy background and card with gold accents, sky-blue highlights, high contrast text.
    Everything inline-styled, no <style> blocks, table-based layout for email compatibility.
    """
    theme_title = " ".join(word.capitalize() for word in theme.split("-"))

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta charset="utf-8">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
</head>
<body style="margin: 0; padding: 0; background-color: #0A1628; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Segoe UI Emoji', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <!-- Outer dark navy background wrapper -->
    <div style="background-color: #0A1628; padding: 24px 12px; min-height: 100vh;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width: 500px; margin: 0 auto;">

            <!-- Greeting Section -->
            <tr>
                <td style="padding: 0 0 20px 0; text-align: center;">
                    <p style="margin: 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.4; color: #6AAFDB; font-weight: 400;">
                        Good evening! 👋
                    </p>
                </td>
            </tr>

            <!-- Main Card with Gold Border -->
            <tr>
                <td style="background-color: #1a2d4d; border: 3px solid #FFD700; border-radius: 20px; padding: 44px 36px; box-shadow: 0 8px 32px rgba(255, 215, 0, 0.15);">

                    <!-- Decorative Header with Moon -->
                    <p style="margin: 0 0 12px 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; color: #FFD700; letter-spacing: 1.2px; text-transform: uppercase; text-align: center; font-style: italic;">
                        🌙 Tonight's Question for
                    </p>

                    <!-- Child's Name - Prominent -->
                    <p style="margin: 0 0 28px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 32px; font-weight: 700; color: #FFFFFF; text-align: center; line-height: 1.1; letter-spacing: -0.5px;">
                        {child_name}
                    </p>

                    <!-- Theme Pill - Bright Accent -->
                    <div style="text-align: center; margin: 0 0 36px 0;">
                        <span style="display: inline-block; background-color: #FFF5E6; color: #1a2d4d; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 600; padding: 12px 22px; border-radius: 24px; border: 2px solid #FFD700; letter-spacing: 0.3px;">
                            {theme_emoji} &nbsp; {theme_title}
                        </span>
                    </div>

                    <!-- Main Question - Large, Highly Legible -->
                    <p style="margin: 0 0 36px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 28px; line-height: 1.6; font-weight: 700; color: #FFFFFF; text-align: center; letter-spacing: -0.3px;">
                        {question}
                    </p>

                    <!-- Divider - Gold to Sky Blue -->
                    <div style="height: 2px; background: linear-gradient(90deg, transparent, #FFD700, #6AAFDB, transparent); margin: 0 0 32px 0;"></div>

                    <!-- Parent Tip Section - Sky Blue Tint -->
                    <div style="background-color: rgba(106, 175, 219, 0.15); border-left: 5px solid #FFD700; padding: 18px 18px; border-radius: 12px; margin: 0;">
                        <!-- Theme Label -->
                        <p style="margin: 0 0 10px 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 700; color: #FFD700; letter-spacing: 0.5px; text-transform: uppercase;">
                            {theme_emoji} &nbsp; {theme_title}
                        </p>
                        <!-- Tip Content -->
                        <p style="margin: 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #E6F0F7;">
                            <span style="font-weight: 700; color: #FFD700; font-style: italic;">💡 Why this helps:</span><br style="margin: 4px 0;">
                            <span style="font-size: 13px; color: #FFF5E6;">{tip}</span>
                        </p>
                    </div>

                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="padding: 20px 0 0 0; text-align: center;">
                    <p style="margin: 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 12px; line-height: 1.5; color: #6AAFDB; font-weight: 400;">
                        Sent {date_str} • A daily moment to help {child_name} shine ✨
                    </p>
                </td>
            </tr>

        </table>
    </div>
</body>
</html>"""

    return html

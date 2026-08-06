def render_email(
    question: str, tip: str, theme: str, child_name: str, date_str: str, theme_emoji: str = "✨"
) -> str:
    """
    Render a dainty, feminine HTML email with pink background and white content card.
    Large grey borders, mobile-optimized, high contrast for dark mode.
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
<body style="margin: 0; padding: 0; background-color: #f8d5e8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Segoe UI Emoji', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <!-- Outer pink background wrapper -->
    <div style="background-color: #f8d5e8; padding: 24px 12px; min-height: 100vh;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width: 500px; margin: 0 auto;">

            <!-- Greeting Section -->
            <tr>
                <td style="padding: 0 0 20px 0; text-align: center;">
                    <p style="margin: 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.4; color: #8a6a8a; font-weight: 400;">
                        Good evening! 👋
                    </p>
                </td>
            </tr>

            <!-- Main Card with Large Grey Border -->
            <tr>
                <td style="background-color: #ffffff; border: 8px solid #9a9a9a; border-radius: 28px; padding: 44px 36px; box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);">

                    <!-- Decorative Header with Moon -->
                    <p style="margin: 0 0 12px 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; color: #d6336c; letter-spacing: 1.2px; text-transform: uppercase; text-align: center; font-style: italic;">
                        🌙 Tonight's Question
                    </p>

                    <!-- Child's Name - Dainty and Prominent -->
                    <p style="margin: 0 0 28px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 32px; font-weight: 700; color: #d6336c; text-align: center; line-height: 1.1; letter-spacing: -0.5px;">
                        for {child_name}
                    </p>

                    <!-- Theme Pill - Dainty -->
                    <div style="text-align: center; margin: 0 0 36px 0;">
                        <span style="display: inline-block; background-color: #fff5f8; color: #c2255c; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 600; padding: 12px 22px; border-radius: 24px; border: 2px solid #e8b8d8; letter-spacing: 0.3px;">
                            {theme_emoji} &nbsp; {theme_title}
                        </span>
                    </div>

                    <!-- Main Question - Large, Elegant, Centered -->
                    <p style="margin: 0 0 36px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 28px; line-height: 1.6; font-weight: 700; color: #3a2233; text-align: center; letter-spacing: -0.3px;">
                        {question}
                    </p>

                    <!-- Delicate Divider -->
                    <div style="height: 2px; background: linear-gradient(90deg, transparent, #e8b8d8, #e8b8d8, #e8b8d8, transparent); margin: 0 0 32px 0;"></div>

                    <!-- Parent Tip Section - Soft Background -->
                    <div style="background-color: #fff5f8; border-left: 5px solid #d6336c; padding: 18px 18px; border-radius: 12px; margin: 0;">
                        <p style="margin: 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #6b4a6b;">
                            <span style="font-weight: 700; color: #d6336c; font-style: italic;">💡 Why this helps:</span><br style="margin: 4px 0;">
                            <span style="font-size: 13px; color: #7a5a7a;">{tip}</span>
                        </p>
                    </div>

                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="padding: 20px 0 0 0; text-align: center;">
                    <p style="margin: 0; font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 12px; line-height: 1.5; color: #a88a98; font-weight: 400;">
                        Sent {date_str} • A daily moment to help {child_name} shine ✨
                    </p>
                </td>
            </tr>

        </table>
    </div>
</body>
</html>"""

    return html

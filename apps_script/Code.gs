const SHEET_ID = PropertiesService.getUserProperties().getProperty('SHEET_ID') || '';
const SHEET_TAB = 'Subscribers';

const VALID_TIMEZONES = [
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Phoenix',
  'America/Los_Angeles',
  'America/Anchorage',
  'Pacific/Honolulu',
  'UTC'
];

function doPost(e) {
  try {
    // Parse the request body
    const data = JSON.parse(e.postData.contents);

    // Honeypot check: if 'website' field is filled, silently return success without touching the sheet
    if (data.website && data.website.trim()) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'ok' }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Validate required fields
    const errors = [];
    if (!data.parent_email || !data.parent_email.trim()) {
      errors.push('parent_email is required');
    }
    if (!data.child_name || !data.child_name.trim()) {
      errors.push('child_name is required');
    }
    if (!data.desired_time || !data.desired_time.trim()) {
      errors.push('desired_time is required');
    }
    if (!data.timezone || !data.timezone.trim()) {
      errors.push('timezone is required');
    }

    if (errors.length > 0) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', errors: errors }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.parent_email)) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', errors: ['Invalid email format'] }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Validate desired_time format (HH:MM 24-hour)
    const timeRegex = /^([01]\d|2[0-3]):[0-5]\d$/;
    if (!timeRegex.test(data.desired_time)) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', errors: ['Invalid time format (expected HH:MM)'] }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Validate timezone against whitelist
    if (!VALID_TIMEZONES.includes(data.timezone)) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', errors: ['Invalid timezone'] }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Open the sheet and get the Subscribers tab
    const ss = SpreadsheetApp.openById(SHEET_ID);
    const sheet = ss.getSheetByName(SHEET_TAB);
    if (!sheet) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', errors: ['Sheet tab not found'] }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Upsert: find existing row by parent_email
    const allData = sheet.getRange(2, 1, sheet.getLastRow() - 1, sheet.getLastColumn()).getValues();
    let foundRowIndex = -1;
    for (let i = 0; i < allData.length; i++) {
      if (allData[i][1] === data.parent_email) {  // Column B is parent_email (index 1)
        foundRowIndex = i;
        break;
      }
    }

    const timestamp = new Date().toISOString();
    const newRow = [
      timestamp,
      data.parent_email,
      data.child_name,
      data.desired_time,
      data.timezone,
      'TRUE',
      ''  // last_sent_date starts empty
    ];

    if (foundRowIndex >= 0) {
      // Update existing row in place (reset last_sent_date to empty on upsert)
      const rowNum = foundRowIndex + 2;  // +1 for header, +1 for 1-indexing
      sheet.getRange(rowNum, 1, 1, newRow.length).setValues([newRow]);
    } else {
      // Append new row
      sheet.appendRow(newRow);
    }

    return ContentService.createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', errors: [error.toString()] }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

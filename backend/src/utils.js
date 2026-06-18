const moment = require('moment-timezone');

// Convert local time to UTC
function localToUTC(localTime, timezone) {
  return moment.tz(localTime, 'YYYY-MM-DDTHH:mm:ss', timezone).utc();
}

// Convert UTC to local time
function utcToLocal(utcTime, timezone) {
  return utcTime.clone().tz(timezone);
}

// Get date in specific timezone
function getDateInTimezone(date, timezone) {
  return moment.tz(date, timezone).format('YYYY-MM-DD');
}

// Calculate minutes between two times
function minutesBetween(fromTime, toTime) {
  return toTime.diff(fromTime, 'minutes');
}

// Format time for display (local time)
function formatTime(isoTime, timezone) {
  const local = moment.tz(isoTime, 'YYYY-MM-DDTHH:mm:ss', timezone);
  return local.format('HH:mm');
}

// Format date for display
function formatDate(isoDate) {
  return moment(isoDate, 'YYYY-MM-DD').format('MMM DD, YYYY');
}

// Format duration as HhMm
function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins}m`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
}

module.exports = {
  localToUTC,
  utcToLocal,
  getDateInTimezone,
  minutesBetween,
  formatTime,
  formatDate,
  formatDuration
};

const fs = require('fs');
const path = require('path');

const sessionsDir = path.join(__dirname, '../sessions');
const outputFile = path.join(__dirname, '../session-list.json');

fs.readdir(sessionsDir, (err, files) => {
  if (err) {
    console.error('Error reading sessions directory:', err);
    process.exit(1);
  }

  const jsonlFiles = files.filter(file => file.endsWith('.jsonl') && !file.startsWith('.'));

  fs.writeFile(outputFile, JSON.stringify(jsonlFiles.sort(), null, 2), (err) => {
    if (err) {
      console.error('Error writing session list file:', err);
      process.exit(1);
    }
    console.log(`Successfully generated session list at ${outputFile}`);
  });
});

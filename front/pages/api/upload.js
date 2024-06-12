import { exec } from 'child_process';
import formidable from 'formidable-serverless';
import fs from 'fs';
import path from 'path';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  console.log("Handling request");
  if (req.method === 'POST') {
    const form = new formidable.IncomingForm();
    form.uploadDir = "../uploads";
    form.keepExtensions = true;
    form.parse(req, (err, fields, files) => {
      if (err) {
        return res.status(500).json({ error: err.message });
      }
      
      const { callId, agentName } = fields;
      const filePath = files.file.path;

      // Path to the script and constructing the command
      const command = `cd .. && poetry run python call_analytics analyze front/'${filePath}' --call-id '${callId}' --agent-name '${agentName}'`;

      exec(command, (error, stdout, stderr) => {
        if (error) {
          return res.status(500).json({ error: error.message });
        }
        if (stderr) {
          return res.status(500).json({ error: stderr });
        }
        res.status(200).json({ message: 'File uploaded and script executed', output: stdout });
      });
    });
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}

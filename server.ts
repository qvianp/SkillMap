import express from 'express';
import http from 'http';
import { execFile, spawn } from 'child_process';
import type { ChildProcess } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.PORT_OVERRIDE || 3000);
const FLASK_HOST = '127.0.0.1';
const FLASK_PORT = Number(process.env.FLASK_PORT || 5001);
const PYLIBS_DIR = path.join(__dirname, '.pylibs');

let flaskProcess: ChildProcess | null = null;
let flaskReady = false;
let startupPromise: Promise<void> | null = null;
let startupError: string | null = null;

function buildPythonEnv(): NodeJS.ProcessEnv {
  const existingPythonPath = process.env.PYTHONPATH || '';
  const pythonPath = existingPythonPath
    ? `${PYLIBS_DIR}${path.delimiter}${existingPythonPath}`
    : PYLIBS_DIR;

  return {
    ...process.env,
    PYTHONPATH: pythonPath,
    FLASK_HOST,
    FLASK_PORT: String(FLASK_PORT),
    FLASK_DEBUG: '0',
    PYTHONUNBUFFERED: '1',
  };
}

async function isFlaskImportable(env: NodeJS.ProcessEnv): Promise<boolean> {
  try {
    await execFileAsync('python3', ['-c', 'import flask, werkzeug, jinja2'], {
      cwd: __dirname,
      env,
      timeout: 5000,
    });
    return true;
  } catch {
    return false;
  }
}

async function ensurePythonDependencies(): Promise<void> {
  const env = buildPythonEnv();
  if (await isFlaskImportable(env)) {
    return;
  }

  console.log('[skillmap] Flask not found; bootstrapping Python dependencies into .pylibs...');
  fs.mkdirSync(PYLIBS_DIR, { recursive: true });

  // Ensure pip is available (install via get-pip.py using stdlib urllib if absent)
  try {
    await execFileAsync('python3', ['-m', 'pip', '--version'], { cwd: __dirname, env, timeout: 5000 });
  } catch {
    console.log('[skillmap] pip not found; installing pip...');
    await execFileAsync(
      'python3',
      [
        '-c',
        [
          'import urllib.request, tempfile, subprocess, sys, os',
          'fd, p = tempfile.mkstemp(suffix=".py")',
          'os.close(fd)',
          'urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", p)',
          'subprocess.check_call([sys.executable, p, "--break-system-packages", "--quiet"])',
          'os.remove(p)',
        ].join('; '),
      ],
      { cwd: __dirname, env, timeout: 60000 }
    );
  }

  const reqFile = path.join(__dirname, 'requirements.txt');
  const pipArgs = fs.existsSync(reqFile)
    ? ['-m', 'pip', 'install', '--no-cache-dir', '--quiet', '--target', PYLIBS_DIR, '-r', reqFile]
    : ['-m', 'pip', 'install', '--no-cache-dir', '--quiet', '--target', PYLIBS_DIR, 'Flask==3.1.0'];

  await execFileAsync('python3', pipArgs, { cwd: __dirname, env, timeout: 120000 });

  if (!(await isFlaskImportable(env))) {
    throw new Error('Flask installation completed, but module import still failed.');
  }
  console.log('[skillmap] Python dependencies installed successfully.');
}

function startFlaskProcess(): void {
  if (flaskProcess) {
    return;
  }

  const env = buildPythonEnv();
  flaskProcess = spawn('python3', ['app.py'], {
    cwd: __dirname,
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  flaskProcess.stdout?.on('data', (chunk: Buffer) => {
    process.stdout.write(`[flask] ${chunk.toString()}`);
  });

  flaskProcess.stderr?.on('data', (chunk: Buffer) => {
    process.stderr.write(`[flask] ${chunk.toString()}`);
  });

  flaskProcess.on('exit', (code) => {
    flaskReady = false;
    flaskProcess = null;
    console.log(`[flask] exited with code ${code}`);
  });
}

function waitForFlask(timeoutMs = 20000): Promise<void> {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const probe = () => {
      const req = http.get(
        { host: FLASK_HOST, port: FLASK_PORT, path: '/careers/', timeout: 1000 },
        (res) => {
          res.resume();
          flaskReady = true;
          resolve();
        }
      );
      req.on('error', () => {
        if (Date.now() - started >= timeoutMs) {
          reject(new Error('Timed out waiting for Python Flask backend.'));
          return;
        }
        setTimeout(probe, 150);
      });
    };
    probe();
  });
}

async function ensureFlaskRunning(): Promise<void> {
  if (flaskReady && flaskProcess) {
    return;
  }
  if (!startupPromise) {
    startupPromise = (async () => {
      try {
        startupError = null;
        await ensurePythonDependencies();
        startFlaskProcess();
        await waitForFlask();
      } catch (err) {
        startupError = err instanceof Error ? err.message : String(err);
        throw err;
      } finally {
        startupPromise = null;
      }
    })();
  }
  return startupPromise;
}

function shutdownFlask(): void {
  if (flaskProcess && !flaskProcess.killed) {
    flaskProcess.kill('SIGTERM');
    flaskProcess = null;
  }
}

process.on('SIGINT', () => {
  shutdownFlask();
  process.exit(0);
});

process.on('SIGTERM', () => {
  shutdownFlask();
  process.exit(0);
});

const app = express();

// Reverse proxy every HTTP request directly to the Python Flask server,
// preserving cookies, redirects, headers, and request bodies verbatim.
app.use(async (req, res) => {
  if (!flaskReady) {
    try {
      await ensureFlaskRunning();
    } catch (err) {
      const msg = startupError || (err instanceof Error ? err.message : 'Backend unavailable');
      res.status(503).send(`SkillMap backend is initializing (${msg}). Please refresh in a moment.`);
      return;
    }
  }

  const headers: http.OutgoingHttpHeaders = { ...req.headers };
  headers.host = req.headers.host || `${FLASK_HOST}:${FLASK_PORT}`;
  if (!headers['x-forwarded-proto']) {
    headers['x-forwarded-proto'] = req.protocol;
  }
  if (!headers['x-forwarded-host'] && req.headers.host) {
    headers['x-forwarded-host'] = req.headers.host;
  }

  const proxyReq = http.request(
    {
      host: FLASK_HOST,
      port: FLASK_PORT,
      path: req.originalUrl,
      method: req.method,
      headers,
    },
    (proxyRes) => {
      res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
      proxyRes.pipe(res, { end: true });
    }
  );

  proxyReq.on('error', (err) => {
    console.error('[proxy error]', err.message);
    flaskReady = false;
    if (!res.headersSent) {
      res.status(502).send('Unable to reach SkillMap Flask backend.');
    }
  });

  req.pipe(proxyReq, { end: true });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`SkillMap proxy listening on http://0.0.0.0:${PORT}`);
  ensureFlaskRunning().catch((err) => {
    console.error('[skillmap] Background Flask startup error:', err);
  });
});

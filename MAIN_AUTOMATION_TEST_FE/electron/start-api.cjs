const { spawn } = require('child_process');
const path = require('path');

const root = path.resolve(__dirname, '../../MAIN_AUTOMATION_TEST');
const child = spawn('python', ['-m', 'api'], {
  cwd: root,
  stdio: 'inherit',
  shell: true,
  env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
});

child.on('exit', (code) => process.exit(code ?? 0));

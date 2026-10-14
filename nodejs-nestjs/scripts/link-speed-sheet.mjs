import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')

const targetDir = path.resolve(rootDir, 'node_modules/@speed-sheet')
const sourceCore = path.resolve(rootDir, '../../speed-sheet/packages/core')
const sourceShared = path.resolve(rootDir, '../../speed-sheet/packages/shared')

if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true })
}

function link(name, src) {
  const dest = path.join(targetDir, name)
  try {
    fs.rmSync(dest, { recursive: true, force: true })
  } catch {}
  fs.symlinkSync(src, dest, 'junction')
  console.log(`[link-speed-sheet] Linked @speed-sheet/${name} -> ${src}`)
}

link('core', sourceCore)
link('shared', sourceShared)

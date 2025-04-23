const fs = require('fs');
const path = require('path');

// Path to the original index.tsx
const originalIndexPath = path.resolve(__dirname, '../src/index.tsx');
// Path to the GitHub Pages entry point
const githubPagesEntryPath = path.resolve(__dirname, '../src/GithubPagesEntry.tsx');
// Backup path for the original index.tsx
const backupIndexPath = path.resolve(__dirname, '../src/index.tsx.backup');

// Backup the original index.tsx
console.log('Backing up original index.tsx...');
fs.copyFileSync(originalIndexPath, backupIndexPath);

// Replace index.tsx with GithubPagesEntry.tsx
console.log('Replacing index.tsx with GithubPagesEntry.tsx for GitHub Pages build...');
const githubPagesContent = fs.readFileSync(githubPagesEntryPath, 'utf8');
fs.writeFileSync(originalIndexPath, githubPagesContent);

// Run the build command
console.log('Running build command...');
const { execSync } = require('child_process');
try {
  execSync('npm run build --legacy-peer-deps', { stdio: 'inherit' });
  console.log('Build completed successfully!');
} catch (error) {
  console.error('Build failed:', error);
} finally {
  // Restore the original index.tsx
  console.log('Restoring original index.tsx...');
  fs.copyFileSync(backupIndexPath, originalIndexPath);
  fs.unlinkSync(backupIndexPath);
  console.log('Original index.tsx restored.');
}

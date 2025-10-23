# Creating a GitHub Release for MakeSomeNoise

This guide explains how to create a GitHub Release and upload the executable for easy distribution.

## Why Use GitHub Releases?

- ✅ Proper way to distribute binary executables
- ✅ Doesn't bloat the git repository
- ✅ Users get direct download links
- ✅ Automatic version tracking
- ✅ Release notes for changelog

## Step-by-Step Release Process

### 1. Ensure Everything is Committed

```powershell
git status  # Should show "working tree clean"
```

### 2. Build the Executable

```powershell
.\build_executable.ps1
```

Verify the executable is at: `dist\MakeSomeNoise.exe`

### 3. Test the Executable

```powershell
.\dist\MakeSomeNoise.exe
```

Make sure it works correctly before releasing!

### 4. Create a GitHub Release

#### Option A: Via GitHub Web Interface (Recommended)

1. Go to your repository: https://github.com/AMoorer/PKFX_Tools

2. Click on **"Releases"** (right sidebar or top navigation)

3. Click **"Create a new release"** or **"Draft a new release"**

4. **Create/Choose a tag**:
   - Tag version: `v1.0.0` (follow semantic versioning)
   - Target: `main` branch
   - Click "Create new tag: v1.0.0 on publish"

5. **Release title**: `MakeSomeNoise v1.0.0`

6. **Description** (example):
   ```markdown
   # MakeSomeNoise v1.0.0 - Initial Release
   
   Procedural noise generator with seamless tiling support.
   
   ## ✨ Features
   - 7 noise types (Perlin, Simplex, FBM, Turbulence, Ridged, Domain Warp, 3D Slice)
   - Industry-standard seamless tiling with adjustable blend width
   - Real-time preview with parameter adjustment
   - Dual-layer noise mixing with blend modes
   - Animation support with texture atlas export
   - 3D offset navigation
   - Export up to 4096×4096 resolution
   
   ## 📥 Installation
   
   **Requirements:** Windows 10/11 (64-bit)
   
   1. Download `MakeSomeNoise.exe` below
   2. (Optional) Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) if you get DLL errors
   3. Double-click to run - no installation needed!
   
   ## 🐛 Known Issues
   - First run may be slow due to Windows Defender scanning (~10-30 seconds)
   - Add to Windows Defender exclusions for faster subsequent runs
   
   ## 📖 Documentation
   See [README.md](https://github.com/AMoorer/PKFX_Tools#readme) for full usage guide.
   ```

7. **Attach the executable**:
   - Click "Attach binaries by dropping them here or selecting them"
   - Upload `dist\MakeSomeNoise.exe`
   - The file will be uploaded and appear in the assets list

8. **Set as latest release**: Check "Set as the latest release"

9. **Publish release**: Click **"Publish release"**

#### Option B: Via GitHub CLI (Advanced)

```powershell
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Login
gh auth login

# Create release with executable
gh release create v1.0.0 `
    dist\MakeSomeNoise.exe `
    --title "MakeSomeNoise v1.0.0" `
    --notes "Initial release with seamless tiling support"
```

### 5. Verify the Release

1. Go to your repository's Releases page
2. You should see your new release
3. The executable should be listed under "Assets"
4. Click the download link to test

### 6. Update README Links (Already Done)

The README already points to:
```markdown
[Releases](../../releases)
```

This automatically links to your releases page!

## Release Checklist

Before publishing a release:

- [ ] All code is committed and pushed
- [ ] Executable builds without errors
- [ ] Executable has been tested and works
- [ ] Version number is updated (if applicable)
- [ ] Release notes are prepared
- [ ] Tag follows semantic versioning (v1.0.0, v1.1.0, etc.)
- [ ] Changelog mentions all new features/fixes

## Version Numbering (Semantic Versioning)

- **v1.0.0** - Initial release
- **v1.0.1** - Bug fixes only
- **v1.1.0** - New features, backward compatible
- **v2.0.0** - Breaking changes

## Future Releases

For subsequent releases:

1. Make your code changes
2. Commit and push
3. Rebuild executable: `.\build_executable.ps1`
4. Create new release with incremented version
5. Add changelog describing what changed

Example changelog format:
```markdown
## What's Changed
- Added new noise type: Voronoi
- Fixed seam artifacts at high blend widths
- Improved export performance by 30%
- Updated UI with new color scheme

## Bug Fixes
- Fixed crash when exporting at 4096×4096
- Fixed memory leak in animation export
```

## Editing/Deleting Releases

- **Edit**: Click the pencil icon on the release
- **Delete**: Click "Delete this release" at the bottom
- **Delete tag**: `git push --delete origin v1.0.0`

## Tips

1. **Draft releases first**: Use "Save draft" to prepare release notes before publishing
2. **Pre-releases**: Check "This is a pre-release" for beta versions
3. **Multiple files**: Upload additional files (documentation, source code zip, etc.)
4. **Automatic notes**: GitHub can auto-generate release notes from commits
5. **Security**: Scan executable with antivirus before uploading

## Common Issues

**Release not showing up:**
- Refresh the page
- Check you selected the correct repository
- Ensure you clicked "Publish release" not "Save draft"

**Can't upload executable (too large):**
- GitHub allows up to 2GB per file
- Your executable (~116MB) is well within limits

**Download statistics:**
- View download counts in the release's "Assets" section
- Helps track adoption

## Example Release Notes Template

```markdown
# MakeSomeNoise vX.X.X

Short description of this release.

## 🎉 New Features
- Feature 1
- Feature 2

## 🐛 Bug Fixes
- Fix 1
- Fix 2

## 🔧 Improvements
- Improvement 1
- Improvement 2

## 📥 Download
Download `MakeSomeNoise.exe` below and run it - no installation needed!

**Requirements:** Windows 10/11 (64-bit)

## 📖 Documentation
See the [README](https://github.com/AMoorer/PKFX_Tools#readme) for full documentation.
```

---

**Ready to create your first release?** Follow the steps above and your executable will be available for download! 🚀

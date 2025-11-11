# MakeSomeNoise v1.1.2 is Here! 🎉

Hey everyone! I'm excited to share that **MakeSomeNoise v1.1.2** just dropped, and this one's packed with some really cool updates.

## What's MakeSomeNoise?

If you're not familiar, MakeSomeNoise is a free tool I built for generating procedural noise textures. Think Perlin noise, Simplex, FBM—all that good stuff that makes your game worlds, VFX, and 3D art look way more interesting. It's a standalone Windows app, so no Python installation or command-line wizardry required. Just download and run.

## What's New in v1.1.2?

### Built-in Learning Guide 📚

This was a big one for me. I added a complete **"Guide To Noise"** right in the app. Click the help button and you get detailed explanations for every noise algorithm—the history, how it works, when to use it, and pro tips. I wanted to make this tool educational, not just functional. Whether you're learning about noise for the first time or just need a quick refresher on what "octaves" actually do, it's all there.

### Export Previews & Animation Playback 🎬

You can now preview your exports before committing! Want to see what that 16-frame atlas will look like? Preview it. Need to check your animation sequence? Play it back at any FPS from 1-60. There's also a handy right-click menu for copying the preview to clipboard or jumping straight to your export folder.

### Smarter File Management 📂

The app now automatically manages file versions for you (_v00, _v01, etc.), so you'll never accidentally overwrite that perfect noise pattern you made. Export paths are also fully visible now—no more mystery directories.

### Cleaner, Smoother Experience ✨

I've been squashing bugs and polishing the UI. Better tooltips everywhere, improved thread management (no more crashes when you spam those sliders), and generally just a more responsive app. Oh, and I removed the redundant "3D Slice" noise type since you can already do that with offset animations.

## The Licensing Thing

Quick note: The **app itself** is free to use for anything, including commercial projects. You just can't sell the app or bundle it for profit without asking me first. But here's the cool part—**anything you generate with it** (textures, images, animations) is completely yours under CC0. Use them commercially, sell them, make NFTs, whatever. No attribution needed (though it's always appreciated 😊).

## Download It!

Ready to generate some noise? Head over to the **[GitHub Release Page](https://github.com/AMoorer/PKFX_Tools/releases/tag/v1.1.2)** and grab the executable. It's a single 120MB file—download, double-click, and you're good to go.

First run might take a few seconds while Windows Defender does its thing, but after that it's smooth sailing.

## Behind the Scenes

For the nerds (and future me who forgets this stuff), this release also includes a complete repository restructure to industry-standard layout. Everything's organized properly now: `src/`, `docs/`, `scripts/`, `tests/`. I even wrote a code review document because I'm apparently that kind of person now.

## What's Next?

I've got a [roadmap](https://github.com/AMoorer/PKFX_Tools/blob/main/docs/ROADMAP.md) brewing with some exciting stuff for v1.2.0—more noise types (Voronoi/Worley, curl noise, billowed), procedural shapes with SDFs, alpha channel support, and maybe even normal map generation. If you've got ideas or feature requests, hit me up on GitHub!

## Try It Out!

If you're doing any kind of procedural generation work—game dev, VFX, generative art, whatever—give MakeSomeNoise a spin. It's free, it's fast, and now it comes with its own tutorial built in.

**Download**: [MakeSomeNoise v1.1.2 on GitHub](https://github.com/AMoorer/PKFX_Tools/releases/tag/v1.1.2)

Happy noise-making! 🎨

---

*- Andy*

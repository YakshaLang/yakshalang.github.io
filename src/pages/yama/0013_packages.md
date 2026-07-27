---
title: Introducing a Package Management System for Yaksha
author: Dean Hunter
status: draft
description: "A package management system."
layout: '../../layouts/YamaPostLayout.astro'
---

# YAMA 0002 - Package Management for Yaksha

- Author(s): Dean Hunter
- Status: 

## Introduction

Package management for programming languages has largely depended on decentralized, Git-based systems as its cost effective. However, this approach has often mandated building from source as commiting large binary files is not typical in Git (most packages arent using GitLFS), this introduces significant delays when dealing with large external sources like Terraform or Boost—especially when initiating a build for the first time, migrating to a new build machine without cached builds. While source-based management suits smaller, self-contained packages, its efficiency is questionable for those with substantial native (C/C++) dependencies.

Often these same languages typically use pre-build scripts as a delivery method for larger dependencies however these scripts are problematic and require maintaining a separate file/script to ensure that the package builds and that the server delivering the artifacts is actually running during the pre-build step.

## The Proposal

I suggest first a method to pull zip/tar files from a http link as a delivery method of package management. Ideally yaksha would be aware of this method and incorporate the required files somewhere in the build, but this likely isnt required for early versions. 

I believe a NuGet's style approach for package architecture, which utilizes a zip-like package format seems to be the most compelling model for streamlining the distribution, versioning, and dependency management of packages with native libraries (it contains sub-folders for each cpu architecture and OS etc). By integrating a similar system within Yaksha, we can simplify the consumption of packages that include native C dependencies. Importantly, this system could complement—rather than replace—the any ideas for source-based package management, offering the flexibility to incorporate larger artifacts within a CI pipeline or pull/build locally from source smaller packages with few native dependencies arent so large.

## Recommendations

### Suggestion 1: Introduction of a `yaksha.json` File

A `yaksha.json` file, akin to NuGet's `.nuspec`, could be introduced, detailing a package's metadata, dependencies, and content. Alternatively, packages could be automatically discovered based on the presence of such file extensions etc within a designated directory.

```json
{
  "name": "PackageName",
  "version": "1.0.0",
  "sha256": "HASH",
  "url": "http://example.com/package.zip",
  "files": ["src/file1.yaka", "src/file2.yaka", "lib/boost.dll", "lib/boost.a"]
}
```

**Pros:** Simplifies locating package content.  
**Cons:** Each new version requires manual metadata updates.

### Suggestion 2: Implementing `yak get` for Seamless Package Management

A `yaksha get` command could be developed to fetch, verify, and unpack packages as per the `yaksha.json` specifications, thereby meshing neatly with the current Yaksha workflow.

```bash
yaksha get PackageName
```

This functionality would adapt based on the URL's suffix, distinguishing between zip/tar formats and source packages needing compilation.

**Pros:** Streamlines use and enhances workflow integration.  
**Cons:** Adds complexity to implementation.

### Suggestion 3: Automated Dependency Management During Builds

By automating external dependency fetches and caching them through the build process, we further refine developer experience.

```json
dependencies {
  package "PackageName", "1.0.0"
}
```

**Pros:** Streamlines dependency management.  
**Cons:** Necessitates comprehensive build system reworks, positioning it as a more long-term objective.

### Suggestion 4: Establishing a Central Package Registry

Mirroring NuGet.org and similar systems, a central registry for Yaksha packages—either as a dynamic server or a static file (list) repository updated via Git—would centralize package distribution and discovery.

**Pros:** Enhances package discoverability and dissemination.  
**Cons:** Requires dedicated infrastructure and upkeep.

## Conclusion

The implementation of `yaksha get` (Suggestion 2) seems to be a balanced and practical early implementation approach, making seamless integration into existing workflows easier. By allowing differentiation based on URL extensions, Yaksha can flexibly support both source-based and pre-compiled package management methodologies. Ideally the "pull from zip" style packagement should be quite simple and assume that the content inside is already functional/verified (such features could be added in the future). This would hopefully accommodate the incorporation of larger C/C++ projects within Yaksha packages, aiming towards an optimized package management ecosystem.

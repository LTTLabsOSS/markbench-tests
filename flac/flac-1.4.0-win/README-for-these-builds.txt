This package contains Windows builds of FLAC 1.4.0

The directories Win32 and Win64 contain 32-bit and 64-bit builds
respectively. Each directory contains flac.exe, metaflac.exe,
libFLAC.dll and libFLAC++.dll. The executables depend on libFLAC.dll
but not on libFLAC++.dll. If you just need the executables to work,
you can delete libFLAC++.dll

All files should work with all versions of Windows going back to (and
including) Windows XP, as long as the CPU has at least SSE2.

Manuals for the flac and metaflac executables can be found in the
manuals directory. The .md files can be opened within any text editor
such as notepad.

README-for-the-project.md explains what the FLAC project is about, and
which parts are licensed under which license. The four COPYING files
contain the licenses mentioned. The AUTHORS file is a text file
crediting various contributors to the FLAC projects.

Note that the README-for-the-project.md file comes directly from the
source code and refers to a few files and documents not included in
this package.
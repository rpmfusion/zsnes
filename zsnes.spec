%define pkgversion %(echo %version|sed s/\\\\\.//)
%define pkgsubdir %(echo %version|sed s/\\\\\./_/)

Summary: ZSNES is a Super Nintendo emulator
Name: zsnes
Version: 1.51
Release: 4%{?dist}
License: GPLv2
Group: Applications/Emulators
URL: http://www.zsnes.com/
Source: http://dl.sf.net/%{name}/%{name}%{pkgversion}src.tar.bz2
# Source Mage
Patch1: zsnes-1.51-Makefile.in.FIX.BROKENESS.patch
# Hans de Goede
Patch2: zsnes-1.51-FORTIFY_SOURCE.patch
# Paul Bender (minimyth)
Patch3: zsnes-1.51-gcc43.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
# This is to build only for i386 on plague
#ExclusiveArch: %{ix86}
ExclusiveArch: i386
BuildRequires: automake
BuildRequires: nasm
BuildRequires: SDL-devel >= 1.2.0
BuildRequires: zlib-devel >= 1.2.3
BuildRequires: libpng-devel >= 1.2.0
BuildRequires: libGL-devel
BuildRequires: ncurses-devel
BuildRequires: libao-devel
BuildRequires: desktop-file-utils
Requires: hicolor-icon-theme

%description
This is an emulator for Nintendo's 16 bit console, called Super Nintendo 
Entertainment System or Super Famicom. It features a pretty accurate emulation
of that system's graphic and sound capabilities.
The GUI enables the user to select games, change options, enable cheat codes 
and to save the game state, even network play is possible.

%prep
%setup -q -n %{name}_%{pkgsubdir}/src
%patch1 -p2
%patch2 -p2
%patch3 -p2

# Remove hardcoded CFLAGS and LDFLAGS
sed -i \
  -e 's:^\s*CFLAGS=.* -D__RELEASE__.*$:CFLAGS="$CFLAGS -D__RELEASE__":' \
  -e 's:^\s*CFLAGS=.* -I\/usr\/local\/include .*$:CFLAGS="${CFLAGS} -I.":' \
  -e '/^\s*LDFLAGS=.* -L\/usr\/local\/lib /d' \
  configure.in

# Fix line encodings in docs/readme.txt/*
sed -i 's/\r//' ../docs/readme.txt/*.txt

# Fix char encondigs
iconv --from=ISO-8859-1 --to=UTF-8 ../docs/readme.txt/games.txt > ../docs/readme.txt/games.txt.utf8
mv ../docs/readme.txt/games.txt.utf8 ../docs/readme.txt/games.txt
iconv --from=ISO-8859-1 --to=UTF-8 ../docs/readme.txt/support.txt > ../docs/readme.txt/support.txt.utf8
mv ../docs/readme.txt/support.txt.utf8 ../docs/readme.txt/support.txt

#  Remove icon extension from desktop file
sed -i -e 's/^Icon=%{name}.png$/Icon=%{name}/g' \
  linux/%{name}.desktop

%build
aclocal
autoconf
%configure \
  --enable-libao \
  --enable-release \
  --disable-cpucheck force_arch="%{_arch}"
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install \
  --vendor dribble \
  --remove-category Application \
  --dir %{buildroot}%{_datadir}/applications \
  linux/%{name}.desktop

# install icons
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48,64x64}/apps
install -m 644 icons/16x16x32.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/zsnes.png
install -m 644 icons/32x32x32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/zsnes.png
install -m 644 icons/48x48x32.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/zsnes.png
install -m 644 icons/64x64x32.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/zsnes.png

%clean
rm -rf %{buildroot}

%post
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
    %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%postun
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
    %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%files
%defattr(-,root,root)
%{_bindir}/zsnes
%{_mandir}/man1/zsnes.1*
%{_datadir}/applications/dribble-%{name}.desktop
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
%doc ../docs/authors.txt ../docs/license.txt ../docs/README.LINUX
%doc ../docs/support.txt ../docs/thanks.txt ../docs/todo.txt
%doc ../docs/readme.htm/ ../docs/readme.txt/

%changelog
* Wed Jul 30 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 1.51-4
- rebuild for buildsys cflags issue

* Tue Jul 22 2008 Andrea Musuruane <musuruan@gmail.com> 1.51-3
- used a workaround to build only for i386 on plague

* Fri Mar 21 2008 Andrea Musuruane <musuruan@gmail.com> 1.51-2
- enabled libao
- changed license due to new guidelines
- added a patch by Paul Bender to compile with gcc 4.3
- removed icon extension from desktop file to match Icon Theme Specification
- removed %%{?dist} tag from changelog
- updated icon cache scriptlets to be compliant to new guidelines
- fixed char encodings in docs
- cosmetic changes

* Thu Mar 01 2007 Andrea Musuruane <musuruan@gmail.com> 1.51-1
- updated to 1.51
- distfile is now a .tar.bz2 instead of a .tar.gz
- added zlib 1.2.3 or greater to BR, now required by ZSNES
- added missing libGL-devel to BR
- added missing hicolor-icon-theme to Requires
- now using new desktop file supplied by upstream (but patched)
- dropped --add-category X-Fedora from desktop-file-install
- fixed line encodings in docs/readme.txt/*
- updated doc files
- removed no longer needed patches
- removed hardcoded CFLAGS and LDFLAGS in %%prep (taken from Gentoo)
- added a new patch from Hans de Goede to compile with -DFORTIFY_SOURCE used
  in %%configure

* Mon Nov 13 2006 Andrea Musuruane <musuruan@gmail.com> 1.42-2
- added missing desktop-file-utils to BuildRequires

* Sun Nov 12 2006 Andrea Musuruane <musuruan@gmail.com> 1.42-1
- initial package
- used a patch from Source Mage to handle @bindir@ and @mandir@ in Makefile
- used a patch from Hans de Goede to compile with -DFORTIFY_SOURCE used
  in %%configure
- used a patch from Erik Musick via Gentoo #117771 to fix a QA notice on 
  executable stack (otherwise running with SELinux enabled breaks)
- used a patch from Leonardo Boshell via Gentoo #125861 to fix a memory 
  corruption bug
- used a patch from Gentoo to fix configure
- used a patch from Terran Melconian via Debian #199461 to fix loading and 
  saving of state files (integrated into Hans' patch otherwise they would 
  conflict)
- used a patch from upstream CVS to fix 100% CPU problem while in GUI 
  (see Debian #319299)


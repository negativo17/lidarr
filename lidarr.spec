%global debug_package %{nil}
%define _build_id_links none

%global user %{name}
%global group %{name}

%global dotnet 3.1

%ifarch x86_64
%global rid x64
%endif

%ifarch aarch64
%global rid arm64
%endif

%ifarch armv7hl
%global rid arm
%endif

Name:           lidarr
Version:        0.8.1.2135
Release:        3%{?dist}
Summary:        Automated manager and downloader for Music
License:        GPLv3
URL:            https://radarr.video/

BuildArch:      x86_64 aarch64 armv7hl

Source0:        https://github.com/%{name}/Lidarr/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source10:       %{name}.service
Source11:       %{name}.xml

BuildRequires:  dotnet-sdk-%{dotnet}
BuildRequires:  firewalld-filesystem
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  systemd
BuildRequires:  tar
BuildRequires:  yarn

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       libmediainfo
Requires:       sqlite
Requires(pre):  shadow-utils

%if 0%{?rhel} >= 8 || 0%{?fedora}
Requires:       (%{name}-selinux if selinux-policy)
%endif

Obsoletes:      %{name} < %{version}-%{release}

%description
Lidarr is a Music recored for Usenet and BitTorrent users. It can monitor
multiple RSS feeds for new music and will grab, sort and rename it. It can also
be configured to automatically upgrade the quality of files already downloaded
when a better quality format becomes available.

%prep
%autosetup -n Lidarr-%{version}

sed -i \
    -e 's/<AssemblyVersion>.*<\/AssemblyVersion>/<AssemblyVersion>%{version}<\/AssemblyVersion>/g' \
    -e 's/<AssemblyConfiguration>.*<\/AssemblyConfiguration>/<AssemblyConfiguration>master<\/AssemblyConfiguration>/g' \
    src/Directory.Build.props

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
dotnet publish \
    --configuration Release \
    --framework netcoreapp%{dotnet} \
    --runtime linux-%{rid} \
    src/Lidarr.sln

yarn install --frozen-lockfile
yarn run build --mode production

%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_prefix}/lib/firewalld/services
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a _output/netcoreapp%{dotnet}/linux-%{rid}/publish %{buildroot}%{_libdir}/%{name}
cp -a _output/Lidarr.Update/netcoreapp%{dotnet}/linux-%{rid}/publish %{buildroot}%{_libdir}/%{name}/Lidarr.Update
cp -a _output/UI %{buildroot}%{_libdir}/%{name}/UI

install -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -m 0644 -p %{SOURCE11} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

find %{buildroot} -name "*.pdb" -delete
find %{buildroot} -name "ServiceUninstall*" -delete
find %{buildroot} -name "ServiceInstall*" -delete
find %{buildroot} -name "Lidarr.Windows*" -delete

%pre
getent group %{group} >/dev/null || groupadd -r %{group}
getent passwd %{user} >/dev/null || \
    useradd -r -g %{group} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "%{name}" %{user}
exit 0

%post
%systemd_post %{name}.service
%firewalld_reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE.md
%doc README.md
%attr(750,%{user},%{group}) %{_sharedstatedir}/%{name}
%{_libdir}/%{name}
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
* Fri Apr 23 2021 Simone Caronni <negativo17@gmail.com> - 0.8.1.2135-3
- Do not create build-id links if no debug package is generated.

* Wed Apr 21 2021 Simone Caronni <negativo17@gmail.com> - 0.8.1.2135-2
- Revert the last change as the runtime is tied to the minor release.

* Mon Apr 19 2021 Simone Caronni <negativo17@gmail.com> - 0.8.1.2135-1
- Update to 0.8.1.2135.
- Add SELinux requirements.
- Build framework dependent binary from source instead of using self contained
  binaries (66% size reduction).

* Sun Mar 07 2021 Simone Caronni <negativo17@gmail.com> - 0.8.0.2042-2
- Switch to Net core build and move installation to libdir.

* Tue Feb 02 2021 Simone Caronni <negativo17@gmail.com> - 0.8.0.2042-1
- Update to 0.8.0.2042.

* Thu Nov 05 2020 Simone Caronni <negativo17@gmail.com> - 0.7.2.1878-1
- Update to 0.7.2.1878.

* Wed Oct 02 2019 Simone Caronni <negativo17@gmail.com> - 0.7.1.1381-1
- Update to 0.7.1.1381.

* Mon May 27 2019 Simone Caronni <negativo17@gmail.com> - 0.6.2.883-1
- Update to 0.6.2.883.

* Tue Apr 30 2019 Simone Caronni <negativo17@gmail.com> - 0.6.1.830-1
- Update to 0.6.1.830.

* Sun Dec 09 2018 Simone Caronni <negativo17@gmail.com> - 0.5.0.583-1
- Update to 0.5.0.583.

* Thu Sep 27 2018 Simone Caronni <negativo17@gmail.com> - 0.4.0.524-1
- Update to 0.4.0.524.

* Tue Jul 24 2018 Simone Caronni <negativo17@gmail.com> - 0.3.1.471-1
- Update to 0.3.1.471.

* Fri Jul 20 2018 Simone Caronni <negativo17@gmail.com> - 0.3.0.430-1
- First build.

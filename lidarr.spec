%global debug_package %{nil}
%define _build_id_links none

%global user %{name}
%global group %{name}

%global dotnet 6.0

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
Version:        1.0.1.2578
Release:        1%{?dist}
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
%if 0%{?rhel} >= 8 || 0%{?fedora} >= 36
BuildRequires:  nodejs >= 17
%else
BuildRequires:  nodejs
%endif
BuildRequires:  systemd
BuildRequires:  tar
BuildRequires:  yarnpkg

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       libmediainfo
Requires:       sqlite
Requires(pre):  shadow-utils

%if 0%{?rhel} >= 8 || 0%{?fedora}
Requires:       (%{name}-selinux if selinux-policy)
%endif

%description
Lidarr is a Music recored for Usenet and BitTorrent users. It can monitor
multiple RSS feeds for new music and will grab, sort and rename it. It can also
be configured to automatically upgrade the quality of files already downloaded
when a better quality format becomes available.

%prep
%autosetup -n Lidarr-%{version}

# Remove test coverage and Windows specific stuff from project file
pushd src
dotnet sln Lidarr.sln remove \
  NzbDrone.Api.Test \
  NzbDrone.Automation.Test \
  NzbDrone.Common.Test \
  NzbDrone.Core.Test \
  NzbDrone.Host.Test \
  NzbDrone.Integration.Test \
  NzbDrone.Libraries.Test \
  NzbDrone.Mono.Test \
  NzbDrone.Test.Common \
  NzbDrone.Test.Dummy \
  NzbDrone.Update.Test \
  NzbDrone.Windows.Test \
  NzbDrone.Windows \
  ServiceHelpers/ServiceInstall \
  ServiceHelpers/ServiceUninstall
popd

%build
pushd src
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
dotnet publish \
    --configuration Release \
    --framework net%{dotnet} \
    --output _output \
    --runtime linux-%{rid} \
    --self-contained \
    --verbosity normal \
    Lidarr.sln
popd

# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
%if 0%{?rhel} >= 9 || 0%{?fedora} >= 36
export NODE_OPTIONS=--openssl-legacy-provider
%endif
yarn run build --mode production

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a src/_output/* _output/UI %{buildroot}%{_libdir}/%{name}/

install -D -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 -p %{SOURCE11} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

find %{buildroot} -name "*.pdb" -delete

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
* Sun May 15 2022 Simone Caronni <negativo17@gmail.com> - 1.0.1.2578-1
- Update to 1.0.1.2578.
- Fix build on OpenSSL 3.0 distributions.

* Mon Mar 14 2022 Simone Caronni <negativo17@gmail.com> - 0.8.1.2135-5
- Merge in changes from Radarr.

* Wed Sep 22 2021 Simone Caronni <negativo17@gmail.com> - 0.8.1.2135-4
- Add nodejs explicit depdendency.

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

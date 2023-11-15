# mock configuration:
# - Requires network for running yarn/dotnet build

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

%if 0%{?fedora} >= 36
%global __requires_exclude ^liblttng-ust\\.so\\.0.*$
%endif

Name:           lidarr
Version:        2.0.2.3782
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
BuildRequires:  nodejs
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
export DOTNET_CLI_TELEMETRY_OPTOUT=1
dotnet msbuild -restore src/Lidarr.sln \
    -p:RuntimeIdentifiers=linux-%{rid} \
    -p:Configuration=Release \
    -p:Platform=Posix \
    -v:normal

# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
yarn run build --mode production

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a _output/net%{dotnet}/* _output/UI %{buildroot}%{_libdir}/%{name}/

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
* Wed Nov 15 2023 Simone Caronni <negativo17@gmail.com> - 2.0.2.3782-1
- Update to 2.0.2.3782.

* Mon Oct 30 2023 Simone Caronni <negativo17@gmail.com> - 2.0.0.3707-1
- Update to 2.0.0.3707.

* Tue Oct 17 2023 Simone Caronni <negativo17@gmail.com> - 1.5.0.3654-1
- Update to 1.5.0.3654.

* Tue Oct 03 2023 Simone Caronni <negativo17@gmail.com> - 1.4.4.3614-1
- Update to 1.4.4.3614.

* Fri Sep 22 2023 Simone Caronni <negativo17@gmail.com> - 1.4.3.3586-1
- Update to 1.4.3.3586.

* Mon Sep 11 2023 Simone Caronni <negativo17@gmail.com> - 1.4.2.3576-1
- Update to 1.4.2.3576.
- Change build to more closely match upstream.

* Mon Sep 04 2023 Simone Caronni <negativo17@gmail.com> - 1.4.1.3566-1
- Update to 1.4.1.3566.

* Sun Aug 27 2023 Simone Caronni <negativo17@gmail.com> - 1.4.0.3554-1
- Update to 1.4.0.3554.

* Wed Aug 23 2023 Simone Caronni <negativo17@gmail.com> - 1.3.5.3530-1
- Update to 1.3.5.3530.

* Mon Aug 07 2023 Simone Caronni <negativo17@gmail.com> - 1.3.4.3458-1
- Update to 1.3.4.3458.

* Mon Jul 17 2023 Simone Caronni <negativo17@gmail.com> - 1.3.1.3371-1
- Update to 1.3.1.3371.

* Mon Jul 10 2023 Simone Caronni <negativo17@gmail.com> - 1.3.0.3326-1
- Update to 1.3.0.3326.

* Tue Jul 04 2023 Simone Caronni <negativo17@gmail.com> - 1.2.6.3313-1
- Update to 1.2.6.3313.

* Thu Jun 22 2023 Simone Caronni <negativo17@gmail.com> - 1.2.5.3288-1
- Update to 1.2.5.3288.

* Mon Jun 12 2023 Simone Caronni <negativo17@gmail.com> - 1.2.4.3273-1
- Update to 1.2.4.3273.

* Tue Jun 06 2023 Simone Caronni <negativo17@gmail.com> - 1.2.3.3267-1
- Update to 1.2.3.3267.

* Tue May 23 2023 Simone Caronni <negativo17@gmail.com> - 1.2.1.3216-1
- Update to 1.2.1.3216.

* Tue May 16 2023 Simone Caronni <negativo17@gmail.com> - 1.2.0.3183-1
- Update to 1.2.0.3183.

* Thu Apr 27 2023 Simone Caronni <negativo17@gmail.com> - 1.1.4.3027-1
- Udpate to 1.1.4.3027.

* Fri Feb 24 2023 Simone Caronni <negativo17@gmail.com> - 1.1.3.2982-1
- Update to 1.1.3.2982.

* Sun Jan 22 2023 Simone Caronni <negativo17@gmail.com> - 1.1.2.2935-1
- Update to 1.1.2.2935.

* Sun Nov 06 2022 Simone Caronni <negativo17@gmail.com> - 1.1.1.2762-1
- Update to 1.1.1.2762.

* Fri Oct 28 2022 Simone Caronni <negativo17@gmail.com> - 1.1.0.2649-3
- Add note about mock configuration.
- Trim changelog.

* Wed Oct 26 2022 Simone Caronni <negativo17@gmail.com> - 1.1.0.2649-2
- Drop OpenSSL workaround.

* Tue Aug 16 2022 Simone Caronni <negativo17@gmail.com> - 1.1.0.2649-1
- Update to 1.1.0.2649.

* Thu Jun 16 2022 Simone Caronni <negativo17@gmail.com> - 1.0.2.2592-1
- Update to 1.0.2.2592.
- Fix issues with LTTng Userspace Tracer library 2.13+.

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

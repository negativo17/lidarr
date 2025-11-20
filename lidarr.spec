# mock configuration:
# - Requires network for running yarn/dotnet build

%global debug_package %{nil}
%define _build_id_links none

%global user %{name}
%global group %{name}

%global dotnet 8.0

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
Version:        3.1.0.4875
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
Requires:       %{name}-selinux

%description
Lidarr is a Music recored for Usenet and BitTorrent users. It can monitor
multiple RSS feeds for new music and will grab, sort and rename it. It can also
be configured to automatically upgrade the quality of files already downloaded
when a better quality format becomes available.

%prep
%autosetup -p1 -n Lidarr-%{version}

# Accomodate old SDK versions
rm -f global.json

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
    -p:SelfContained=true \
    -v:normal

# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
yarn run build --mode production

find . -name libcoreclrtraceptprovider.so -delete

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a _output/net*/* _output/UI %{buildroot}%{_libdir}/%{name}/

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
* Thu Nov 20 2025 Simone Caronni <negativo17@gmail.com> - 3.1.0.4875-1
- Update to 3.1.0.4875.

* Sun Nov 09 2025 Simone Caronni <negativo17@gmail.com> - 3.0.1.4866-1
- Update to 3.0.1.4866.

* Sat Sep 06 2025 Simone Caronni <negativo17@gmail.com> - 2.13.3.4711-2
- Make sure tracerpt is disabled, it requires an old liblttng-ust.

* Thu Sep 04 2025 Simone Caronni <negativo17@gmail.com> - 2.13.3.4711-1
- Update to 2.13.3.4711.

* Fri Jun 13 2025 Simone Caronni <negativo17@gmail.com> - 2.12.4.4658-1
- Update to 2.12.4.4658.

* Sun May 11 2025 Simone Caronni <negativo17@gmail.com> - 2.11.2.4629-1
- Update to 2.11.2.4629.

* Sun Apr 13 2025 Simone Caronni <negativo17@gmail.com> - 2.10.3.4602-1
- Update to 2.10.3.4602.

* Tue Mar 11 2025 Simone Caronni <negativo17@gmail.com> - 2.9.6.4552-2
- Fix for GHSA-65x7-c272-7g7r.

* Tue Feb 04 2025 Simone Caronni <negativo17@gmail.com> - 2.9.6.4552-1
- Update to 2.9.6.4552.

* Fri Dec 20 2024 Simone Caronni <negativo17@gmail.com> - 2.8.2.4493-1
- Update to 2.8.2.4493.

* Sun Oct 27 2024 Simone Caronni <negativo17@gmail.com> - 2.7.1.4417-1
- Update to 2.7.1.4417.

* Thu Oct 10 2024 Simone Caronni <negativo17@gmail.com> - 2.6.4.4402-1
- Update to 2.6.4.4402.

* Tue Sep 24 2024 Simone Caronni <negativo17@gmail.com> - 2.6.1.4370-1
- Update to 2.6.1.4370.
- Switch to .NET 8.0.

* Thu Sep 12 2024 Simone Caronni <negativo17@gmail.com> - 2.5.3.4341-1
- Update to 2.5.3.4341.

* Thu Aug 29 2024 Simone Caronni <negativo17@gmail.com> - 2.5.2.4316-1
- Update to 2.5.2.4316.

* Sun Aug 18 2024 Simone Caronni <negativo17@gmail.com> - 2.5.1.4311-1
- Update to 2.5.1.4311.

* Sun Aug 04 2024 Simone Caronni <negativo17@gmail.com> - 2.5.0.4277-1
- Update to 2.5.0.4277.
- Backport patch for https://github.com/advisories/GHSA-63p8-c4ww-9cg7.
- Clean up SPEC file.

* Wed Jul 10 2024 Simone Caronni <negativo17@gmail.com> - 2.4.2.4238-1
- Update to 2.4.2.4238.

* Wed Jul 03 2024 Simone Caronni <negativo17@gmail.com> - 2.4.1.4234-1
- Update to 2.4.1.4234.

* Mon Jun 24 2024 Simone Caronni <negativo17@gmail.com> - 2.4.0.4222-1
- Update to 2.4.0.4222.

* Thu May 16 2024 Simone Caronni <negativo17@gmail.com> - 2.3.3.4204-1
- Update to 2.3.3.4204.

* Wed May 08 2024 Simone Caronni <negativo17@gmail.com> - 2.3.2.4183-1
- Update to 2.3.2.4183.

* Wed Apr 24 2024 Simone Caronni <negativo17@gmail.com> - 2.3.0.4159-1
- Update to 2.3.0.4159.

* Tue Apr 16 2024 Simone Caronni <negativo17@gmail.com> - 2.2.5.4141-1
- Update to 2.2.5.4141.

* Wed Mar 20 2024 Simone Caronni <negativo17@gmail.com> - 2.2.3.4098-1
- Update to 2.2.3.4098.

* Tue Mar 12 2024 Simone Caronni <negativo17@gmail.com> - 2.2.2.4090-1
- Update to 2.2.2.4090.

* Sun Mar 03 2024 Simone Caronni <negativo17@gmail.com> - 2.2.1.4073-1
- Update to 2.2.1.4073.

* Tue Feb 20 2024 Simone Caronni <negativo17@gmail.com> - 2.2.0.4045-1
- Update to 2.2.0.4045.

* Mon Feb 12 2024 Simone Caronni <negativo17@gmail.com> - 2.1.7.4030-1
- Update to 2.1.7.4030.

* Mon Feb 05 2024 Simone Caronni <negativo17@gmail.com> - 2.1.6.3993-1
- Update to 2.1.6.3993.

* Wed Jan 31 2024 Simone Caronni <negativo17@gmail.com> - 2.1.5.3968-1
- Update to 2.1.5.3968.

* Thu Jan 25 2024 Simone Caronni <negativo17@gmail.com> - 2.1.4.3941-1
- Update to 2.1.4.3941.

* Wed Jan 17 2024 Simone Caronni <negativo17@gmail.com> - 2.1.3.3927-1
- Update to 2.1.3.3927.

* Mon Jan 08 2024 Simone Caronni <negativo17@gmail.com> - 2.1.2.3893-1
- Update to 2.1.2.3893.

* Thu Dec 28 2023 Simone Caronni <negativo17@gmail.com> - 2.1.1.3877-1
- Update to 2.1.1.3877.

* Thu Dec 21 2023 Simone Caronni <negativo17@gmail.com> - 2.1.0.3856-1
- Update to 2.1.0.3856.

* Tue Dec 12 2023 Simone Caronni <negativo17@gmail.com> - 2.0.7.3849-1
- Update to 2.0.7.3849.

* Sun Nov 26 2023 Simone Caronni <negativo17@gmail.com> - 2.0.5.3813-1
- Update to 2.0.5.3813.

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
